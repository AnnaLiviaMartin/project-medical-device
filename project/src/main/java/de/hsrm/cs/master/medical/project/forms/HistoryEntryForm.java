package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.HistoryCategory;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;

@Setter
@Getter
public class HistoryEntryForm {

    @NotNull(message = "Date is required.")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate date = LocalDate.now();

    @NotBlank(message = "Title is required.")
    @Size(max = 255, message = "Title may be at most 255 characters long.")
    private String title = "";

    @NotNull(message = "Please select a category.")
    private HistoryCategory category;

    @Size(max = 4000, message = "Description may be at most 4000 characters long.")
    private String description = "";

    @Size(max = 150)
    private String doctor = "";

    @Size(max = 150)
    private String department = "";

}
