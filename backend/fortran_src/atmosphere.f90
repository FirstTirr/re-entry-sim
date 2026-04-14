module atmosphere
    use constants
    implicit none

contains

    subroutine get_atmospheric_properties(h, rho, T, p)
        real(8), intent(in) :: h
        real(8), intent(out) :: rho, T, p
        real(8) :: h_geo, dh, rho_84
        integer :: i
        real(8), parameter :: hb(8) = (/ &
            0.0D0, 11000.0D0, 20000.0D0, 32000.0D0, &
            47000.0D0, 51000.0D0, 71000.0D0, 84852.0D0 /)
        real(8), parameter :: Tb(8) = (/ &
            288.15D0, 216.65D0, 216.65D0, 228.65D0, &
            270.65D0, 270.65D0, 214.65D0, 186.946D0 /)
        real(8), parameter :: Pb(8) = (/ &
            101325.0D0, 22632.06D0, 5474.889D0, 868.0187D0, &
            110.9063D0, 66.93887D0, 3.956420D0, 0.3734D0 /)
        real(8), parameter :: Lb(8) = (/ &
            -0.0065D0, 0.0D0, 0.0010D0, 0.0028D0, &
            0.0D0, -0.0028D0, -0.0020D0, 0.0D0 /)

        h_geo = R_EARTH * h / (R_EARTH + max(h, 0.0D0))

        if (h_geo <= hb(8)) then
            i = 1
            do while (i < 8 .and. h_geo > hb(i + 1))
                i = i + 1
            end do

            dh = h_geo - hb(i)
            if (abs(Lb(i)) > 1.0D-12) then
                T = Tb(i) + Lb(i) * dh
                p = Pb(i) * (Tb(i) / T) ** (G0 / (R_AIR * Lb(i)))
            else
                T = Tb(i)
                p = Pb(i) * exp(-G0 * dh / (R_AIR * T))
            end if
            rho = p / (R_AIR * T)
        else
            T = 186.946D0
            p = Pb(8) * exp(-(h_geo - hb(8)) / 7500.0D0)
            rho_84 = Pb(8) / (R_AIR * T)
            rho = rho_84 * exp(-(h_geo - hb(8)) / 7500.0D0)
        end if

        if (rho < 1.0D-12) rho = 1.0D-12
    end subroutine get_atmospheric_properties

    ! Model Atmosfer: Estimasi Kerapatan (Density) Udara (US Standard Atmosphere 1976 - Simplified)
    subroutine get_atmospheric_density(h, rho)
        real(8), intent(in) :: h
        real(8), intent(out) :: rho
        real(8) :: T, p

        call get_atmospheric_properties(h, rho, T, p)
    end subroutine get_atmospheric_density

    ! Model Kecepatan Suara berdasar suhu atmosfer
    subroutine get_speed_of_sound(h, a)
        real(8), intent(in) :: h
        real(8), intent(out) :: a
        real(8) :: T, rho, p

        call get_atmospheric_properties(h, rho, T, p)
        a = sqrt(GAMMA_AIR * R_AIR * T)
    end subroutine get_speed_of_sound

end module atmosphere
