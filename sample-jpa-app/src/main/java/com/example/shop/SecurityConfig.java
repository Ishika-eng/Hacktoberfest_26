package com.example.shop;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    @Override
    public UserDetailsService userDetailsService() {
        return new InMemoryUserDetailsManager(
            User.withUsername("clerk").password(passwordEncoder().encode("clerk123")).roles("CLERK").build(),
            User.withUsername("manager").password(passwordEncoder().encode("manager123")).roles("MANAGER").build());
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .authorizeRequests()
                .antMatchers("/actuator/health").permitAll()
                .antMatchers("/whoami").permitAll()
                .antMatchers(HttpMethod.POST, "/products").hasAnyRole("CLERK", "MANAGER")
                .antMatchers(HttpMethod.DELETE, "/products/**").hasRole("MANAGER")
                .antMatchers("/actuator/**").hasRole("MANAGER")
                .anyRequest().authenticated()
            .and()
            .httpBasic();
    }
}
