package com.example.demo;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class SecurityTests {

    @Autowired MockMvc mvc;

    @Test void publicIsOpen() throws Exception {
        mvc.perform(get("/public/ping")).andExpect(status().isOk());
    }

    @Test void adminRequiresLogin() throws Exception {
        mvc.perform(get("/admin/secret")).andExpect(status().isUnauthorized());
    }

    @Test @WithMockUser(roles = "USER") void adminForbiddenForUser() throws Exception {
        mvc.perform(get("/admin/secret")).andExpect(status().isForbidden());
    }

    @Test @WithMockUser(roles = "ADMIN") void adminAllowedForAdmin() throws Exception {
        mvc.perform(get("/admin/secret")).andExpect(status().isOk());
    }

    @Test @WithMockUser void validOrderAccepted() throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON)
                .content("{\"item\":\"book\",\"quantity\":2}")).andExpect(status().isOk());
    }

    @Test @WithMockUser void invalidOrderRejected() throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON)
                .content("{\"item\":\"\",\"quantity\":0}")).andExpect(status().isBadRequest());
    }
}
