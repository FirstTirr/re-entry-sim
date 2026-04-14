module trajectory
    use constants
    use atmosphere
    use thermodynamics
    use aerodynamics
    implicit none

contains
    subroutine simulate(v0, gamma0, h0, m0, A, Cd, Q_star, dt, t_max, shape_factor, initial_lat, initial_lon, lift_to_drag, bank_angle_deg, initial_heading_deg, n_steps, time_out, h_out, v_out, m_out, q_out, g_out, lat_out, lon_out, mach_out)
        !f2py intent(in) v0, gamma0, h0, m0, A, Cd, Q_star, dt, t_max, shape_factor, initial_lat, initial_lon, lift_to_drag, bank_angle_deg, initial_heading_deg
        !f2py intent(hide) n_steps
        !f2py intent(out) time_out, h_out, v_out, m_out, q_out, g_out, lat_out, lon_out, mach_out
        real(8), intent(in) :: v0, gamma0, h0, m0, A, Cd, Q_star, dt, t_max, shape_factor, initial_lat, initial_lon
        real(8), intent(in) :: lift_to_drag, bank_angle_deg, initial_heading_deg
        integer, intent(out) :: n_steps
        real(8), intent(out) :: time_out(100000), h_out(100000), v_out(100000), m_out(100000)
        real(8), intent(out) :: q_out(100000), g_out(100000), lat_out(100000), lon_out(100000), mach_out(100000)
        
        real(8) :: t, h, v, m, gamma, rho, D, L, q_dot, m_dot, R_nose
        real(8) :: lat, lon, psi, g_force, a_sound, g_local, v_safe, bank_rad
        real(8) :: v_dot, gamma_dot, h_dot, r_cur, psi_dot, lat_dot, lon_dot, aero_acc
        real(8) :: cos_gamma_safe, cos_lat_safe
        integer :: max_steps, step
        
        R_nose = sqrt(max(A, 1.0D-8) / PI) * max(shape_factor, 1.0D-3)
        max_steps = int(t_max / dt)
        
        t = 0.0D0
        h = h0
        v = v0
        m = m0
        gamma = gamma0
        lat = initial_lat * PI / 180.0D0
        lon = initial_lon * PI / 180.0D0
        psi = initial_heading_deg * PI / 180.0D0
        bank_rad = bank_angle_deg * PI / 180.0D0
        step = 1
        
        do while (t <= t_max .and. h > MIN_ALTITUDE .and. m > MIN_MASS .and. step <= max_steps .and. step <= 100000)
            time_out(step) = t
            h_out(step) = h
            v_out(step) = v
            m_out(step) = m
            lat_out(step) = lat * 180.0D0 / PI
            lon_out(step) = lon * 180.0D0 / PI
            
            call get_atmospheric_density(h, rho)
            call get_speed_of_sound(h, a_sound)
            
            mach_out(step) = abs(v) / max(a_sound, 1.0D-6)
            
            call calculate_aero_forces(rho, abs(v), a_sound, A, Cd, lift_to_drag, D, L)
            call calculate_ablation(abs(v), rho, A, Q_star, R_nose, q_dot, m_dot)
            
            aero_acc = sqrt(D * D + L * L) / max(m, MIN_MASS)
            g_force = aero_acc / G0
            q_out(step) = q_dot
            g_out(step) = g_force
            
            ! Update state
            r_cur = R_EARTH + max(h, 0.0D0)
            g_local = G0 * (R_EARTH / r_cur) ** 2
            v_safe = max(abs(v), 1.0D0)
            cos_gamma_safe = max(abs(cos(gamma)), 1.0D-6)
            cos_lat_safe = max(abs(cos(lat)), 1.0D-6)

            v_dot = -(D / max(m, MIN_MASS)) - g_local * sin(gamma)
            gamma_dot = (L * cos(bank_rad)) / (max(m, MIN_MASS) * v_safe) + cos(gamma) * (v_safe / r_cur - g_local / v_safe)
            psi_dot = (L * sin(bank_rad)) / (max(m, MIN_MASS) * v_safe * cos_gamma_safe)
            h_dot = v_safe * sin(gamma)
            lat_dot = (v_safe * cos(gamma) * cos(psi)) / r_cur
            lon_dot = (v_safe * cos(gamma) * sin(psi)) / (r_cur * cos_lat_safe) - OMEGA_EARTH

            v = max(v + v_dot * dt, 0.0D0)
            gamma = gamma + gamma_dot * dt
            psi = psi + psi_dot * dt
            h = h + h_dot * dt
            lat = lat + lat_dot * dt
            lon = lon + lon_dot * dt
            if (h < MIN_ALTITUDE) h = MIN_ALTITUDE
            m = max(m - (m_dot * dt), MIN_MASS)
            
            if (lat > 0.5D0 * PI) lat = 0.5D0 * PI
            if (lat < -0.5D0 * PI) lat = -0.5D0 * PI
            if (lon > PI) lon = lon - 2.0D0 * PI
            if (lon < -PI) lon = lon + 2.0D0 * PI
            if (psi > PI) psi = psi - 2.0D0 * PI
            if (psi < -PI) psi = psi + 2.0D0 * PI
            
            t = t + dt
            step = step + 1
        end do
        
        n_steps = step - 1
    end subroutine simulate
end module trajectory
