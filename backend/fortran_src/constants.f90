module constants
    implicit none
    ! Konstanta Fisika dan Planet (Bumi)
    real(8), parameter :: G0 = 9.80665D0            ! Gravitasi di permukaan (m/s^2)
    real(8), parameter :: R_EARTH = 6371000.0D0     ! Radius rata-rata Bumi (m)
    real(8), parameter :: RHO0 = 1.225D0            ! Kerapatan udara permukaan (kg/m^3)
    real(8), parameter :: K_SG = 1.74153D-4         ! Konstanta Sutton-Graves untuk atmosfer Bumi
    real(8), parameter :: PI = 3.14159265358979323846D0
    real(8), parameter :: OMEGA_EARTH = 7.2921159D-5 ! Kecepatan rotasi bumi (rad/s)
    real(8), parameter :: R_AIR = 287.05D0          ! Konstanta gas spesifik udara (J/kg/K)
    real(8), parameter :: GAMMA_AIR = 1.4D0         ! Rasio panas spesifik udara
    
    ! Parameter Solver Numrik
    real(8), parameter :: MIN_ALTITUDE = 0.0D0      ! Ketinggian tanah (m)
    real(8), parameter :: MIN_MASS = 1.0D-3         ! Sisa massa minimum (kg) sebelom dianggap hancur sempurna
end module constants
