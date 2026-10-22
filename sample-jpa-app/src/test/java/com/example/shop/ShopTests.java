package com.example.shop;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class ShopTests {

    @Autowired MockMvc mvc;
    @Autowired ProductRepository products;

    @Test void healthIsPublic() throws Exception {
        mvc.perform(get("/actuator/health")).andExpect(status().isOk());
    }

    @Test void otherActuatorEndpointsNeedManager() throws Exception {
        mvc.perform(get("/actuator/info")).andExpect(status().isUnauthorized());
        mvc.perform(get("/actuator/info").with(httpBasic("clerk", "clerk123"))).andExpect(status().isForbidden());
        mvc.perform(get("/actuator/info").with(httpBasic("manager", "manager123"))).andExpect(status().isOk());
    }

    @Test void listingNeedsLogin() throws Exception {
        mvc.perform(get("/products")).andExpect(status().isUnauthorized());
        mvc.perform(get("/products").with(httpBasic("clerk", "clerk123"))).andExpect(status().isOk());
    }

    @Test void clerkCanCreateButNotDelete() throws Exception {
        mvc.perform(post("/products").with(httpBasic("clerk", "clerk123")).contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"pen\",\"price\":1.50,\"description\":\"blue\"}")).andExpect(status().isCreated());
        mvc.perform(delete("/products/1").with(httpBasic("clerk", "clerk123"))).andExpect(status().isForbidden());
    }

    @Test void managerCanDelete() throws Exception {
        Product p = new Product();
        p.setName("temporary");
        Product saved = products.save(p);
        mvc.perform(delete("/products/" + saved.getId()).with(httpBasic("manager", "manager123")))
           .andExpect(status().isOk());
    }

    @Test void blankNameIsRejected() throws Exception {
        mvc.perform(post("/products").with(httpBasic("clerk", "clerk123")).contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\":\"\",\"price\":1}")).andExpect(status().isBadRequest());
    }

    @Test void whoamiReportsTheLoggedInUser() throws Exception {
        mvc.perform(get("/whoami").with(httpBasic("clerk", "clerk123"))).andExpect(status().isOk());
    }

    @Test void longDescriptionsAreStoredInFull() {
        Product p = new Product();
        p.setName("manual");
        p.setDescription("x".repeat(1000));
        Product saved = products.saveAndFlush(p);
        assertEquals(1000, products.findById(saved.getId()).orElseThrow().getDescription().length());
    }
}
