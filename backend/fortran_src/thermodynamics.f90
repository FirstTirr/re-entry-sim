module thermodynamics
    use constants
    implicit none
contains
    ! Menghitung Laju Pemanasan (Heating Rate) dan Ablasi Massa
    ! Menggunakan Sutton-Graves stagnation point convective heating
    subroutine calculate_ablation(v, rho, A, Q_star, R_nose, q_dot, m_dot)
        real(8), intent(in) :: v, rho, A, Q_star, R_nose
        real(8), intent(out) :: q_dot, m_dot
        real(8) :: v_eff, rho_eff, r_eff
        
        ! Laju Fluks Panas Konvektif (W/m^2)
        ! q_dot = K * sqrt(rho/R_nose) * v^3
        v_eff = max(v, 0.0D0)
        rho_eff = max(rho, 1.0D-12)
        r_eff = max(R_nose, 1.0D-3)
        q_dot = K_SG * sqrt(rho_eff / r_eff) * (v_eff**3)
        
        ! Laju perubahan massa (Ablasi) - kg/s
        if (Q_star > 1.0D0) then
            m_dot = (q_dot * max(A, 0.0D0)) / Q_star
        else
            m_dot = 0.0D0
        end if
    end subroutine calculate_ablation
end module thermodynamics
