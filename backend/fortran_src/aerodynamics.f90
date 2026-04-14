module aerodynamics
    implicit none

contains

    ! Menghitung Gaya Hambat (Drag Force) with Dynamic Cd
    subroutine calculate_drag(rho, v, a_sound, A, Cd_base, D)
        real(8), intent(in) :: rho, v, a_sound, A, Cd_base
        real(8), intent(out) :: D
        real(8) :: Mach, Cd_dyn
        
        Mach = v / max(a_sound, 1.0D-6)
        
        ! Transonic & Hypersonic Drag Curve Approximation
        if (Mach > 5.0D0) then
            Cd_dyn = Cd_base
        else if (Mach > 1.2D0) then
            Cd_dyn = Cd_base * (1.6D0 - 0.15D0 * (Mach - 1.2D0))
        else if (Mach > 0.8D0) then
            Cd_dyn = Cd_base * (1.0D0 + 1.5D0 * (Mach - 0.8D0))
        else
            Cd_dyn = Cd_base
        end if
        Cd_dyn = max(Cd_dyn, 0.05D0)
        
        D = 0.5D0 * max(rho, 0.0D0) * (v**2) * Cd_dyn * max(A, 0.0D0)
    end subroutine calculate_drag

    ! Menghitung gaya aerodinamika total (drag + lift)
    subroutine calculate_aero_forces(rho, v, a_sound, A, Cd_base, ld_ratio, D, L)
        real(8), intent(in) :: rho, v, a_sound, A, Cd_base, ld_ratio
        real(8), intent(out) :: D, L

        call calculate_drag(rho, v, a_sound, A, Cd_base, D)
        L = max(ld_ratio, 0.0D0) * D
    end subroutine calculate_aero_forces
end module aerodynamics
