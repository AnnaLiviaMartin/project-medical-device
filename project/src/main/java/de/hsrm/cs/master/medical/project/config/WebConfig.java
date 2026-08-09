package de.hsrm.cs.master.medical.project.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.io.File;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    // TODO anderswo hin?

    @Value("${upload_dir}")
    private String path = "";

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String uploadDir = new File(path).getAbsolutePath();
        registry.addResourceHandler("/media/**").addResourceLocations("file:" + uploadDir + File.separator);
    }
}
