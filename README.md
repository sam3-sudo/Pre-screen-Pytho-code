package com.supp.benefits.adam.service.controller.definition;
import com.supp.benefits.adam.service.model.definition.DefinitionConstructResponse;
import com.supp.benefits.adam.service.model.domain.model.common.DesktopResponse;
import com.supp.benefits.adam.service.model.domain.model.common.Metadata;
import com.supp.benefits.adam.service.modFel.domain.model.common.Outcome;
import com.supp.benefits.adam.service.services.definition.DefinitionService;
import com.supp.benefits.adam.service.services.datadefinitionserviceimpl.DefinitionDataService;
import org.springframework.web.bind.annotation.PostMapping;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections.MapUtils;
import org.apache.commons.lang3.BooleanUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

import static com.supp.benefits.adam.service.common.constants.DefinitionConstants.*;
import static org.springframework.http.HttpStatus.*;
import static sun.security.timestamp.TSResponse.BAD_REQUEST;


@RestController
@RequestMapping(value = "/definition/display")
@Slf4j
public class DefinitionDisplayController {

    @Autowired
    DefintionDataService defintionDataService;

    /**
     * Definition Details Service
     *
     * @param ivGroup
     * @param ivUser
     * @param id
     * @return
     */
    @RequestMapping(value = "/{id}", method = RequestMethod.GET)
    public ResponseEntity<DesktopResponse> getDefinitionDetails(
            @RequestHeader(value = DEFAULT_GROUP_HEADER_NAME, defaultValue = DEFAULT_GROUP_NAME) String ivGroup,
            @RequestHeader(value = DEFAULT_USER_HEADER_NAME, defaultValue = DEFAULT_USER_NAME) String ivUser,
            @PathVariable String id,
            @RequestParam Boolean isLive) {
        final DesktopResponse desktopResponse = defintionDataService.getDefinitionDetails(id, ivGroup, isLive);
        return new ResponseEntity<>(desktopResponse,
                valueOf(Integer.valueOf(desktopResponse.getMetadata().getOutcome().getStatus())));
    }

    /**
     * Create definitions API.
     *
     * @param ivGroup
     * @param ivUser
     * @param definitionXmlMap
     * @return ResponseEntity<DesktopResponse>.
     */
    @PostMapping
    public ResponseEntity<DesktopResponse> createDefinition(
            @RequestHeader(value = DEFAULT_GROUP_HEADER_NAME, defaultValue = DEFAULT_GROUP_NAME) String ivGroup,
            @RequestHeader(value = DEFAULT_USER_HEADER_NAME, defaultValue = DEFAULT_USER_NAME) String ivUser,
            @RequestBody Map<String, Object> definitionXmlMap) {

        log.debug("Service to create a definition invoked...");

        return (MapUtils.isNotEmpty(definitionXmlMap))
                ? new ResponseEntity<>(definitionDataService.create(definitionXmlMap), OK)
                : new ResponseEntity<>(
                new DesktopResponse(new Metadata(new Outcome(String.valueOf(BAD_REQUEST.value()),
                        "Invalid request parameters!")), Collections.<String, String>emptyMap()),
                BAD_REQUEST);
    }


    private HttpStatus getHttpStatus(DefinitionConstructResponse definitionResult) {
        if (definitionResult.getValidationResponse() == null
                || BooleanUtils.isNotTrue(definitionResult.getValidationResponse().getValid())) {
            return BAD_REQUEST;
        } else {
            return OK;
        }
    }

    private Metadata buildMetadata(HttpStatus status, String errorMessage) {
        String message = StringUtils.isEmpty(errorMessage) ? status.name() : errorMessage;
        return new Metadata(new Outcome(String.valueOf(status.value()), message));
    }

    @RequestMapping(value = "{definitionID}/{option}/children", method = RequestMethod.GET)
    @ResponseBody
    public IfpDesktopDisplaySearch retrieveDefChildrenByDefId(
            @RequestHeader(value = "iv-groups", defaultValue = "default_usr") String ivGroup,
            @RequestParam(value = "viewType", required = false) String viewType,
            @RequestParam(value = "viewRole", required = false) String viewRole,
            @PathVariable String definitionID,
            @PathVariable String option,
            HttpServletResponse HTTPResponse) throws IOException {
        IfpDesktopDisplaySearch responseData = new IfpDesktopDisplaySearch();
        Map<String, Object> definitionMap = new HashMap<>();
        Map<String, List<Map<String, Object>>> defDetails =
                new HashMap<>();
        boolean isRWOrROUser = ladyBirdCommons.checkConfigToolUsers(ivGroup, false);
        boolean isWelcomeKitUser = validateUserRolesUtil.isWelcomKitUser(ivGroup);
        boolean isCSBUser = ladyBirdCommons.checkConfigToolUsers(ivGroup, true);

        if (StringUtils.equalsIgnoreCase(option, "sourceMapping")) {
            responseData = fieldsUtil.getDisplaySearchFromFile("/definition/sourceMappingConfig.json", null);
        } else {
            responseData = fieldsUtil.getDisplaySearchFromFile("/definition/definitionTreeConfig.json", null);
        }
    }
