package com.supp.benefits.adam.service.services.ladybird;


import static com.supp.benefits.adam.service.common.constants.DesktopServiceConstants.MESSAGE_KEY;
import static com.supp.benefits.adam.service.common.constants.DesktopServiceConstants._POPULATE_MODEL;
import static com.supp.benefits.adam.service.common.constants.IfpDesktopServicesConstant.*;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.bouncycastle.cms.CMSSignedGenerator.DATA;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.io.IOException;


import com.supp.benefits.adam.service.api.client.definition.OnPremDefinitionDraftClient;
import com.supp.benefits.adam.service.exception.RestException;
import com.supp.benefits.adam.service.model.desktop.domain.Actions;
import com.supp.benefits.adam.service.model.desktop.domain.Fields;
import com.supp.benefits.adam.service.model.desktop.domain.PaginationInfo;
import com.supp.benefits.adam.service.model.desktop.domain.ShowDetailsLink;
import com.supp.benefits.adam.service.services.ladybird.Model.MappingSearchRequestParams;
import com.supp.benefits.adam.service.services.util.Util;
import com.supp.benefits.adam.service.utils.JsonTransformerUtil;
import com.supp.benefits.common.util.exception.BusinessException;
import feign.FeignException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.lang.StringUtils;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;


import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;

@Service
@Slf4j
public class KindredService {


    private static final String PAGINATION = "pagination";
    private static final String MESSAGE = "message";

    @Autowired
    private OnPremDefinitionDraftClient onPremDefinitionDraftClient;


    public Map<String, Object> searchKindred(String ivGroup, String sourceDefinitionID, boolean kindAssociation, String pagination, String pageNum,
                                             String pageSize, String pageCount, String targetDefinitionID, String mappingDefinitionID, String mappingDefinitionName, boolean isRegenerateMapping)
            throws JsonParseException, JsonMappingException, IOException, BusinessException {
        log.info("KindredService.searchKindred called with the data " + sourceDefinitionID);
        Map<String, Object> kindredMappingResponse = new HashMap<String, Object>();
        Integer totalKindredCount = 0;
        Actions actions = new Actions();

        PaginationInfo paginationInfo = Util.calculatePageInfo(pageSize, pageNum, pageCount, pagination);
        Util.getPageStartRow(paginationInfo);

        MappingSearchRequestParams requestParams = new MappingSearchRequestParams(
                sourceDefinitionID, kindAssociation, "SOURCE_GROUP", paginationInfo.getPageSize(), paginationInfo.getPageStartRow()
        );

        Map<String, Object> kindredResultMap = getFormattedSourceFields(requestParams);

        if (kindredResultMap.containsKey(MESSAGE_KEY)) {
            kindredResultMap.put(ACTIONS, new ArrayList<Map<String, Object>>());
            kindredMappingResponse.put(DATA, kindredResultMap);
            if (null == targetDefinitionID)

                return kindredMappingResponse;
            else {
                kindredResultMap.remove(MESSAGE_KEY);                        // From source to target mapping view
                preparekindredViewResponse(sourceDefinitionID,
                        targetDefinitionID, kindredResultMap, actions, mappingDefinitionID, mappingDefinitionName, isRegenerateMapping);
            }
        }

        if (kindredResultMap.containsKey("kindredPaginatedResults")) {
            kindredResultMap.put(ACTIONS, kindredResultMap.get("kindredPaginatedResults"));
        }
        if (kindredResultMap.containsKey("totalKindredCount")) {
            totalKindredCount = (Integer) kindredResultMap.get("totalKindredCount");
        }
        kindredMappingResponse.put(DATA, kindredResultMap);

        String[] headerOrder = {"sourceGroupID", "sourceFieldName", "sourceFieldType", "kindFieldID"};
        if (null != totalKindredCount) {
            paginationInfo.setRecordCount(totalKindredCount);
        }
        paginationInfo.setRequestMethod("GET");
        paginationInfo.setUrl("/usr-desktop-services/ladybird/kindred/display?sourceDefinitionID=" + sourceDefinitionID + "&targetDefinitionID=" + targetDefinitionID + "&kindAssociation=" + kindAssociation);
        paginationInfo.setPageCount(Integer.toString(Util.calculatePageCount(paginationInfo.getPageSize(), totalKindredCount + EMPTY)));
        Util.getNewPageNumber(paginationInfo);

        Fields field = new Fields(COLLECTION, ACTIONS, false, null, null, false);
        field.setFieldToObjectLocation(ACTIONS);
        field.setHeaders(Arrays.asList(headerOrder));
        field.setPageInfo(paginationInfo);
        field.setPagination(JsonTransformerUtil.transformJsonStrToMap(new JSONObject(paginationInfo).toString()));
        actions.addField(field);


        ShowDetailsLink sourceFieldLink;

        kindredMappingResponse.put(ACTIONS, actions);
        kindredMappingResponse.put(PAGINATION, paginationInfo);
        kindredResultMap.put(PAGINATION, paginationInfo);

        if (StringUtils.isNotBlank(targetDefinitionID)) {                                                    // From source to target mapping view
            sourceFieldLink = new ShowDetailsLink("genericAtionDetails", "#/addSource/{definitionID}/sourceToTarget", "redirect", false);
            actions.addLink(sourceFieldLink);

            preparekindredViewResponse(sourceDefinitionID,
                    targetDefinitionID, kindredResultMap, actions, mappingDefinitionID, mappingDefinitionName, isRegenerateMapping);
        } else {
            sourceFieldLink = new ShowDetailsLink("genericAtionDetails", "#/addSource/{definitionID}", "redirect", false);
            actions.addLink(sourceFieldLink);

            kindredResultMap.put(_POPULATE_MODEL, "self");
            ShowDetailsLink showAllSourceFieldsLink = new ShowDetailsLink("showFieldsWithoutKindred", "/usr-desktop-services/ladybird/kindred/display?sourceDefinitionID=" + sourceDefinitionID + "&kindAssociation=false", "GET", false);
            ShowDetailsLink showSourceFieldsWithoutKindredLink = new ShowDetailsLink("showFieldsWithKindred", "/usr-desktop-services/ladybird/kindred/display?sourceDefinitionID=" + sourceDefinitionID + "&kindAssociation=true", "GET", false);
            actions.addLink(showAllSourceFieldsLink);
            actions.addLink(showSourceFieldsWithoutKindredLink);
        }
        kindredResultMap.put(_TEMPLATE, "views/ladybird/kindredmaps");
        kindredMappingResponse.put(HEADER_ORDER, headerOrder);

        return kindredMappingResponse;
    }

    @SuppressWarnings("unchecked")
    private void preparekindredViewResponse(String sourceDefinitionID,
                                            String targetDefinitionID, Map<String, Object> kindredResultMap,
                                            Actions actions, String mappingDefinitionID, String mappingDefinitionName, boolean isRegenerateMapping) {
        kindredResultMap.put("targetDefinitionID", targetDefinitionID);
        kindredResultMap.put("sourceDefinitionID", sourceDefinitionID);

        Fields msgField = new Fields(MESSAGE, MESSAGE, "string", false, false, null, null);
        msgField.setDefaultValue("There are no unmapped fields"); //TODO : A simple msg

        if (kindredResultMap.containsKey(ACTIONS)) {
            List<Map<String, Object>> fieldsList = (ArrayList<Map<String, Object>>) kindredResultMap.get(ACTIONS);
            if (fieldsList.size() == 0) {
                actions.addField(msgField);
                actions.removeField(ACTIONS);
            }
        } else {
            actions.addField(msgField);
            actions.removeField(ACTIONS);
        }
        String uri = "/usr-desktop-services/ladybird/source/mapping/{sourceDefinitionID}/{targetDefinitionID}?definitionId=" + mappingDefinitionID + "&definitionName=" + mappingDefinitionName + "&isRegenerateMapping=";
        if (isRegenerateMapping) {
            uri = uri + "true";
        } else {
            uri = uri + "false";
        }
        ShowDetailsLink continueLink = new ShowDetailsLink("continueMapping", uri, "GET", false);
        actions.addLink(continueLink);
    }


    @SuppressWarnings("unchecked")
    protected Map<String, Object> getFormattedSourceFields(MappingSearchRequestParams requestParams) throws BusinessException {
        Map<String, Object> kindredResultMap = new HashMap<String, Object>();
        List<Map<String, Object>> mappingRuleDefinitions = new ArrayList<>();
        List<Map<String, String>> kindredResults = new ArrayList<Map<String, String>>();
        Integer totalKindredCount = 0;


        try {
            ResponseEntity<Map<String, Object>> mappingSearchResponse = onPremDefinitionDraftClient.mappingSearch(
                    requestParams.getDefinitionId(), requestParams.isAssociation(), requestParams.getDefinitionSubType(),
                    requestParams.getLimit(), requestParams.getOffset());

            mappingRuleDefinitions = (ArrayList<Map<String, Object>>) mappingSearchResponse.getBody().get("searchResult");
            totalKindredCount = (Integer) mappingSearchResponse.getBody().get("resultCount");
        } catch (Exception e) {
            int status = -1;
            if (e instanceof FeignException) {
                status = ((FeignException) e).status();
            } else if (e instanceof RestException) {
                status = ((RestException) e).getHttpStatusCode();
            }

            if (HttpStatus.NOT_FOUND.value() == status) {
                kindredResultMap.put("kindredPaginatedResults", new ArrayList<Map<String, Object>>());
                kindredResultMap.put("totalKindredCount", 0);
                return kindredResultMap;
            } else {
                log.error("Error calling mappingSearch endpoint.", e);
                kindredResultMap.put(MESSAGE_KEY, "Requested search criteria does not have the results");
            }
        }

        if (!mappingRuleDefinitions.isEmpty()) {
            log.info("have appropriate results");
            kindredResults = formatKindreds(mappingRuleDefinitions);
        }

        kindredResultMap.put("kindredPaginatedResults", kindredResults);
        kindredResultMap.put("totalKindredCount", totalKindredCount);
        log.debug("Final results to be displayed on UI " + kindredResultMap);
        return kindredResultMap;
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, String>> formatKindreds(List<Map<String, Object>> definitions) {
        List<Map<String, String>> formattedResponse = new ArrayList<Map<String, String>>();
        Map<String, String> formattedMap = null;
        if (CollectionUtils.isNotEmpty(definitions)) {
            for (Map<String, Object> definition : definitions) {
                if (definition.containsKey("attributes")) {
                    List<Map<String, String>> attributes = (List<Map<String, String>>) definition.get("attributes");
                    formattedMap = new HashMap<String, String>();
                    formattedMap.put("definitionID", (String) definition.get("definitionID"));
                    formattedMap.put("sourceGroupID", (String) definition.get("parentDefinitionID"));
                    for (Map<String, String> attribute : attributes) {
                        if (null != attribute.get("name")) {
                            switch (attribute.get("name")) {
							/*case "parentGroup":
								formattedMap.put("sourceGroupID",attribute.get("value"));
								break;*/
                                case "fieldName":
                                    formattedMap.put("sourceFieldName", attribute.get("value"));
                                    break;
                                case "fieldType":
                                    formattedMap.put("sourceFieldType", attribute.get("value"));
                                    break;
                                case "kindFieldDefinitionID":
                                    formattedMap.put("kindFieldID", attribute.get("value"));
                                    break;
                            }
                        }
                    }
                    formattedResponse.add(formattedMap);
                }
            }
        }
        return formattedResponse;
    }
}

