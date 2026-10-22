package com.example.demo;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class LoginTests {

    @Autowired MockMvc mvc;

    @Test void adminCredentialsOpenAdminArea() throws Exception {
        mvc.perform(get("/admin/secret").with(httpBasic("admin", "admin123"))).andExpect(status().isOk());
    }

    @Test void regularUserCredentialsAreForbidden() throws Exception {
        mvc.perform(get("/admin/secret").with(httpBasic("alice", "alice123"))).andExpect(status().isForbidden());
    }

    @Test void wrongPasswordRejected() throws Exception {
        mvc.perform(get("/admin/secret").with(httpBasic("admin", "nope"))).andExpect(status().isUnauthorized());
    }

    @Test void authenticationManagerAcceptsValidLogin() throws Exception {
        mvc.perform(post("/public/auth-check").param("username", "admin").param("password", "admin123"))
           .andExpect(status().isOk())
           .andExpect(content().string(org.hamcrest.Matchers.containsString("authenticated admin")));
    }

    @Test void authenticationManagerRejectsBadLogin() throws Exception {
        mvc.perform(post("/public/auth-check").param("username", "admin").param("password", "wrong"))
           .andExpect(status().isUnauthorized());
    }
}
