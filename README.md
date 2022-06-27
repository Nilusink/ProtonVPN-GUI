![total lines - Github](https://img.shields.io/tokei/lines/github/Nilusink/ProtonVPN-GUI)
![languages - Github](https://img.shields.io/github/languages/count/Nilusink/ProtonVPN-GUI)
![top language - Github](https://img.shields.io/github/languages/top/Nilusink/ProtonVPN-GUI)
# ProtonVPN-GUI
A ProtonVPN GUI for GNU/Linux. Aimed to imitate the Windows-GUI and fully written in Python.

![map screenshot](https://github.com/Nilusink/ProtonVPN-GUI/blob/main/screenshots/ProtonVPN_GUI_2.png?raw=true)

## Installation
Clone this repository into your desired location using <br>
`git clone https://github.com/Nilusink/ProtonVPN-GUI`

### Setup VPN (first time only)
Since there isn't a login function yet, you will need to run `init.py` and login
using your **OpenVPN** credentials. Those can be found in your **ProtonVPN account settings**
under **OpenVPN / IKEv2**. You will need to run the init file using **superuser** permissions.
(**sudo** / **doas**)

## Running the program
Run
```bash
sudo python3.10 main.pyw
```
in the ProtonVPN-GUI directory. You will need **superuser** permissions, since the
protonvpn_cli library requires them.

## Todo
* Login (setup) built into the GUI
* Further UI improvements