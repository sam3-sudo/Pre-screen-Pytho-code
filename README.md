package com.yourcompany.adam.service.ladybird;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/usr-desktop-services/ladybird/source")
public class SourcePdfUploadController {

    @Autowired
    private SourcePdfUploadService pdfUploadService;

    // POST endpoint to upload PDF
    @PostMapping("/source-pdf-upload")
    public String uploadPdf(@RequestParam("file") MultipartFile file) {
        return pdfUploadService.uploadPdfFile(file);
    }
}

2
service class 
package com.yourcompany.adam.service.ladybird;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
public class SourcePdfUploadService {

    // Define the upload directory (adjust as needed)
    private static final String UPLOAD_DIRECTORY = "/path/to/save/uploads/";

    public String uploadPdfFile(MultipartFile file) {
        try {
            // Define the file path to save
            Path path = Paths.get(UPLOAD_DIRECTORY + file.getOriginalFilename());
            
            // Save the file locally
            Files.write(path, file.getBytes());

            return "File uploaded successfully: " + path.toString();
        } catch (IOException e) {
            return "File upload failed: " + e.getMessage();
        }
    }
}
3
package com.yourcompany.adam.service.ladybird;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/usr-desktop-services/ladybird/source")
public class SourcePdfFileController {

    @Autowired
    private SourcePdfFileService pdfFileService;

    // GET endpoint to retrieve file info
    @GetMapping("/sourcePdfUploadedFile")
    public String getUploadedFileInfo(@RequestParam("fileID") String fileID) {
        return pdfFileService.getFileInfo(fileID);
    }
}
4
package com.yourcompany.adam.service.ladybird;

import org.springframework.stereotype.Service;

@Service
public class SourcePdfFileService {

    public String getFileInfo(String fileID) {
        // Logic to retrieve file details (e.g., from a database or storage)
        // For simplicity, this example returns mock data
        return "{ \"fileID\": \"" + fileID + "\", \"fileName\": \"example.pdf\", \"fileSize\": \"1MB\", \"uploadDate\": \"2024-12-25\" }";
    }
}
