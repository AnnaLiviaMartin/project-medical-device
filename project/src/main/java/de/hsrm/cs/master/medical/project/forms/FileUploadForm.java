package de.hsrm.cs.master.medical.project.forms;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import org.springframework.web.multipart.MultipartFile;

@Setter
@Getter
public class FileUploadForm {
    @NotNull
    private MultipartFile file;
}
