package com.supp.benefits.adam.service.utils;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.joda.JodaModule;
import com.supp.benefits.adam.service.model.desktop.domain.IfpDesktopDisplaySearch;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;


/**
 * Util class for transforming serialized json string objects into Pojo or java util classes and Vice versa
 * @author m37974
 */
@Slf4j
public class JsonTransformerUtil {

    public static final String JODA_DATE_FORMAT = "yyyy-MM-dd";

    /**
     * This method is used for transforming Joda datetimes into appropriate formats
     * @return ObjectMapper mapper
     */
    public static ObjectMapper getObjectMapper(){
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JodaModule());
        mapper.setDateFormat(new SimpleDateFormat(JODA_DATE_FORMAT));
        mapper.setSerializationInclusion(JsonInclude.Include.NON_EMPTY);
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        mapper.configure(DeserializationFeature.ACCEPT_EMPTY_STRING_AS_NULL_OBJECT, true);
        mapper.configure(DeserializationFeature.READ_ENUMS_USING_TO_STRING, true);
        mapper.configure(SerializationFeature.WRITE_ENUMS_USING_TO_STRING, true);
        return mapper;
    }

    /**
     * This method is used for transforming Json formatted String value into
     * HashMap object of String and Object pairs
     * @param requestJson
     * @return
     */
    public static Map<String,Object> transformJsonStrToMap(String requestJson) {
        Map<String, Object> retriggerActionMap = null;
        try {
            retriggerActionMap = getObjectMapper().readValue(requestJson, new TypeReference<HashMap<String,Object>>(){});
        } catch (JsonProcessingException jpe) {
            log.error("JsonTransformerUtil.transferPolicy failed with JsonProcessingException. Details : ", jpe);
        } catch (IOException ioe) {
            log.error("JsonTransformerUtil.transferPolicy failed with IOException. Details : ", ioe);
        }
        return retriggerActionMap;
    }

<<<<<<< SSHARK-330
=======
    /**
     * This method is used for transforming IfpDesktopDisplaySearch Object
     * (which is used to prepare data required as per UI) into JSON formatted String
     * @param response
     * @return
     */
    public static String transferDesktopResponse(IfpDesktopDisplaySearch response){
        String json = null;
        try {
            json = getObjectMapper().writeValueAsString(response);
        } catch (JsonProcessingException e) {
            log.error("JsonTransformerUtil.transferDesktopResponse failed ", e);
        }
        return json;
    }
>>>>>>> main
}
