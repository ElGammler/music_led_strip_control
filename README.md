<h1 align="center">
  Music LED Strip Control (MLSC)
</h1>

<p align="center">
    <img src="https://user-images.githubusercontent.com/24798198/107574531-1d6d7300-6bef-11eb-8d7f-83c42a5784d2.png" alt="Logo" />
</p>

<p align="center">
  <a style="text-decoration:none" href="https://www.python.org/downloads/release/python-3919/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg?color=3498DB&style=flat-square" alt="Python Version" />
  </a>
  <a style="text-decoration:none" href="https://discord.gg/bMmWYGcz/">
    <img src="https://img.shields.io/discord/774182494277992478?color=3498DB&style=flat-square&label=discord" alt="Discord" />
  </a>
  <a style="text-decoration:none" href="https://github.com/TobKra96/music_led_strip_control/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/TobKra96/music_led_strip_control?color=3498DB&style=flat-square" alt="GitHub" />
  </a>
</p>


<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#installing">Installing</a>
      <ul>
        <li><a href="#automated-installation">Automated installation</a></li>
      </ul>
    </li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


## Features

- 🎵 Audio visualization in real time.
- ✨ Modern web interface.
- 📝 REST API with extensive documentation using SwaggerUI.
- 🔒 Optional dashboard PIN lock.
- 📈 System status dashboard.
- 💡 27 effects with many configuration options.
- 🎨 Customizable colors and color schemes.
- ⚡ Multicore optimized for large LED strips (900+ LEDs).
- 🖥️ Multi-device support.
- 🎙️ Standalone and client compatible for audio processing.


## Installing

Please check if your hardware is listed inside the [Compatible Hardware List](https://github.com/TobKra96/music_led_strip_control/wiki/Compatible-Hardware-List).

### Automated installation
Run the following command in your terminal:
```bash
curl -sSL https://raw.githubusercontent.com/TobKra96/music_led_strip_control/master/setup.sh | sudo bash -s -- -b master
```

The script also accepts some options:

* `-b`, `--branch`       git branch to use (`master`, `dev_2.3`)
* `-h`, `--help`         show this list of command-line options

After the installation completes, please check the [Installation Guide](https://github.com/TobKra96/music_led_strip_control/wiki/Installation-Guide#iv-configure-music-led-strip-control) to configure the initial settings.

Also, check out the tutorial video I created for the installation:

<p align="center">
  <a style="text-decoration:none" href="https://youtu.be/ShpOVoOpqrQ">
    <img src="https://user-images.githubusercontent.com/24798198/108500735-87051580-72b0-11eb-8841-65f79421277a.png" alt="Tutorial_Github" />
  </a>
</p>

<h2 align="center">
    Setup schematic
</h2>
<p align="center">
  <a style="text-decoration:none" href="https://github.com/TobKra96/music_led_strip_control/wiki/Installation-Guide">
    <img src="https://user-images.githubusercontent.com/24798198/107310140-209c1e00-6a8c-11eb-8bbb-0e99f63e667c.png" alt="Schematic" />
  </a>
</p>


## Demo

<p align="center">
  <a style="text-decoration:none" href="https://youtu.be/DankmP4riOo">
    <img src="https://user-images.githubusercontent.com/24798198/108499122-24127f00-72ae-11eb-8668-7c720f527c46.png" alt="Version2_Github" />
  </a>
  <a style="text-decoration:none" href="https://youtu.be/eUSX9l89th0">
    <img src="https://user-images.githubusercontent.com/24798198/108499722-0abe0280-72af-11eb-9dc1-f37e3df0b0e7.png" alt="Roomtour_Github" />
  </a>
  <a style="text-decoration:none" href="https://youtu.be/jAL1DfeYQI8">
    <img src="https://user-images.githubusercontent.com/24798198/108499975-68eae580-72af-11eb-9115-594b11f503cf.png" alt="Version1_Github" />
  </a>
  <a style="text-decoration:none" href="">
    <img src="https://user-images.githubusercontent.com/24798198/112079905-48999980-8b81-11eb-846f-30a475092874.png" alt="Mockup" />
  </a>
</p>


## Acknowledgements

* [Audio Reactive LED Strip by Scott Lawson](https://github.com/scottlawsonbc/audio-reactive-led-strip)

Thank you for the digital signal processing and some effects. You are the best.

* [rpi_ws281x by Jeremy Garff](https://github.com/jgarff/rpi_ws281x)

Awesome library for the LED output signal. Easy to use.

* [Flask Datta Able by CodedThemes](https://appseed.us/admin-dashboards/flask-datta-able)

Flask admin dashboard.

Scripts included:

[Bootstrap](https://getbootstrap.com/docs/4.6/),
[jQuery](https://jquery.com/),
[jQuery-Scrollbar](https://github.com/gromo/jquery.scrollbar/),
[jQuery-UI](https://jqueryui.com/),
[Pickr](https://github.com/Simonwep/pickr),
[Font Awesome](https://fontawesome.com),
[Tagin](https://github.com/erwinheldy/tagin)


## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/TobKra96/music_led_strip_control/blob/master/LICENSE) for more information.
