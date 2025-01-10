 @RequestMapping(value = "sourcePdfUploadedFile", method = RequestMethod.POST, produces = MediaType.TEXT_PLAIN)
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    public @ResponseBody String uploadSourceFile(
            @RequestParam("sourceFile") MultipartFile uploadedFile,
            @RequestParam("definitionID") String definitionID,
            @RequestParam("definitionName") String definitionName,
            @RequestParam("generateSourceFields") String generateSourceFields,
            @RequestParam("release") String releaseDefinitionId,
            @RequestParam("sourceData") String sourceData,
            @RequestHeader(value = "iv-user", defaultValue = "default_usrId") String userId,
            @RequestHeader(value = "iv-groups", defaultValue = "default_usr") String ivGroup,
            HttpServletResponse HTTPResponse) throws IOException, SystemException, RestException {

        HashMap<String, Object> sourceObject = (HashMap<String, Object>) JsonTransformerUtil
                .transformJsonStrToMap(sourceData);
        IfpDesktopDisplaySearch ifpDesktopDisplaySearch = new IfpDesktopDisplaySearch();
        Boolean fileUploadSuccess = false;
        Map<String, Object> data = new HashMap<String, Object>();
        data.put(DEFINITION_ID, definitionID);
        data.put(DEFINITION_NAME, definitionName);
        data.put("release", releaseDefinitionId);

        String respongMsg = null;
        File sourceFile = new File(uploadedFile.getOriginalFilename());
        String uploadedFileName = sourceFile.getName();
        String responseString = null;
        String payloadUUID = null;
        try {
            String fileData = new String(Base64.encodeBase64(uploadedFile
                    .getBytes()));
            ResponseEntity<String> responseEntity;

            Map<String, String> headers = new HashMap<>();
            headers.put("X-User", userId);
            headers.put("X-Definition-FileName", uploadedFileName);
            headers.put("X-Source-DefinitionId", definitionID);
            headers.put("X-Release-DefinitionId", releaseDefinitionId);
            headers.put(HttpHeaders.CONTENT_TYPE, MediaType.TEXT_XML);

            responseEntity = retailFileUtilClient.saveFile(fileData, generateSourceFields, headers);

            if (HttpStatus.OK.equals(responseEntity.getStatusCode()) && null != responseEntity.getBody()) {
                responseString = responseEntity.getBody();
                Document document = XMLUtil.buildDocFromString(responseString);
                NodeList payloadDataInstncID = document
                        .getElementsByTagName("fileUtil:payloadDataInstncID");
                if (null != payloadDataInstncID.item(0)) {
                    payloadUUID = payloadDataInstncID.item(0)
                            .getTextContent();
                }
                String failedFields = "";
                NodeList errorDefinitions = document
                        .getElementsByTagName("fileUtil:errorDefinition");

                for (int i = 0; i < errorDefinitions.getLength(); i++) {
                    Element element = (Element) errorDefinitions.item(i);
                    NamedNodeMap attributes = element.getAttributes();
                    if (null != attributes.item(0)) {
                        Attr attr = (Attr) attributes.item(0);
                        String attrValue = attr.getNodeValue();
                        failedFields = failedFields + "," + attrValue;
                    }

                }

                sourceObject.put("templateFileName", uploadedFileName);
                sourceObject.put("templateFileID", payloadUUID);
                // Save Source with Uploaded file details
                saveResourceData(ivGroup, userId, sourceObject);
                if (errorDefinitions.getLength() <= 0) {
                    respongMsg = "File successfully uploaded";
                    fileUploadSuccess = true;
                } else {
                    respongMsg = "File was not successfully uploaded, there were "
                            + failedFields
                            + " fields that were not able to be created, please select another PDF file or try again";
                }
            } else {
                respongMsg = "File was not successfully uploaded,invalid content found, please select valid PDF file";
            }

        } catch (IOException | RestException e) {
            log.error("Exception", e);
            throw e;
        }
        data.put("generateSourceFields", generateSourceFields);
        data.put("sourceData", new JSONObject(sourceObject).toString());
        data.put("_populateModel", "self");
        if (fileUploadSuccess) {
            data.put(_REDIRECT, "#/addSource/" + definitionID); //edit source
        }
        data.put("_mesage", respongMsg);

        ifpDesktopDisplaySearch.setData(data);
        JSONObject resultJson = new JSONObject(ifpDesktopDisplaySearch);

        return resultJson.toString();
    }
}
