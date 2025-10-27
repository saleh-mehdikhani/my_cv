+++
title = "Projects"
+++

Here are some of my notable projects:

## Electrical Automotive Firmware: [Confidential]
**Technologies:** C, Bazel, Scons

**Descriptions:** Contributed to the development of an electric vehicle software platform, focusing on build system integration using Bazel and SCons. Worked in an agile, cross-cultural team with a U.S. customer to maintain multiple coexisting build systems, resolve dependency conflicts, and ensure continuous compatibility with a fast-evolving upstream codebase. Also supported new feature development and build optimization tasks.

---

## AoA Firmware Development: [CoreHW]
**Technologies:** C, BLE, Embedded Linux, MQTT

**Description:** Led the firmware team in developing **CoreHW’s next-generation indoor positioning system** based on a proprietary BLE protocol. Enhanced a sample system to support **multi-device full-duplex communication** while relaying IQ samples to MQTT in real time. Performed system-level analysis to identify and resolve bottlenecks, optimizing capacity and reliability. Actively contributed to overall system design and collaborated closely with a medium-sized cross-functional team to deliver a robust and high-performance firmware solution.

[View on DigiKey](https://www.digikey.fi/en/products/detail/corehw-semiconductor-ltd/CHW-LOC4000-1-0/25956605) | [Demo](https://youtu.be/YSwqVEpV4Z0?si=-dtOhvAG3SJdJZJE)

---

## AI/ML TPMS: [Unikie]
**Technologies:** C, Edge AI (TensorFlow Lite), BLE

**Description:** Developed an **edge ML-based BLE direction-finding system** running entirely on the MCU. Tuned AoA signal sampling, trained a machine learning model, and deployed it for on-device direction detection. Overcame signal noise challenges with a post-processing function that aggregates recent AI outputs for accurate estimation. Results were successfully demonstrated at Embedded World 2025.

[View on Unikie](https://www.unikie.com/stories/unikie-silicon-labs-creating-on-device-ai-solutions/) | [Demo](https://www.linkedin.com/posts/siliconlabs_unikie-and-silicon-labs-creating-on-device-activity-7328094842075389952-ctR1?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAyjNPcBqOD7mJK-hYBv61OwPQUX9NlBXMI)

---

## AoA SDK Sample: [onsemi]
**Technologies:** C, CMSIS Pack, BLE

**Description:** Developed firmware for **BLE AoA positioning on RSL15** microcontrollers, implemented in Embedded C on top of the CMSIS Pack SDK. Delivered a complete AoA sample for both transmitter and receiver, which was **published as the official Onsemi SDK example**. Contributed to multi-sync support, resource management without an OS, and overall system design in collaboration with the customer. Overcame challenges in compatibility with SDK examples and constrained MCU resources to ensure robust and standards-compliant functionality.

[View on onsemi](https://www.onsemi.com/company/news-media/press-announcements/en/onsemi-launches-end-to-end-positioning-system-to-enable-accurate-more-power-efficient-asset-tracking) | [Demo](https://youtu.be/Vo_pDct5TBM?si=Xa8ptH9vvSCCmzvM)

---

## Zephyr AoA Firmware: [CoreHW]
**Technologies:** C, Zephyr, BLE, Multi-Threaded

**Description:** Designed and implemented firmware for nRF52 series microcontrollers to enable BLE 5 AoA positioning, building on Zephyr OS. Developing a **multi-device operation and maximized IQ sample throughput**, overcoming early Zephyr limitations for AoA on nRF52833. Contributed fixes upstream to the Zephyr project and led the **software architecture design**, including multi-threading management, resource optimization, and reliable signal handling. This firmware formed the second generation of CoreHW’s publicly available AoA system.

---

## Security Platform: [Confidential]
**Technologies:** C, CMake, OpTEE

**Description:** Developed and integrated a security platform based on OpTee for a proprietary product. Focused on resolving integration issues, and producing clean, maintainable CMake build scripts. Worked closely in a small team to ensure a robust and reliable secure firmware foundation.

---

## Smart Home Devices: [Hinava]
**Technologies:** C, C++, BLE, WiFi, ZigBee

**Description:** Served as the technical leader and embedded developer for a commercial smart home system. Designed the **system architecture** and developed devices using Zigbee (TI chipset), BLE (TI chipset), and WiFi (Espressif). Focused on **mass-production readiness, optimizing for **low power consumption**, cost efficiency, and real-time, stable communication across multiple protocols. Successfully delivered a commercial product now available in the market.

[View on Hinava](https://www.hinava.com/)

---

## Other Projects: [Unikie Customers]
**Technologies:** C, C++, Python

**Description:** Worked on a range of projects spanning industrial automation, research, and telecommunications, including:

- **Image Processing for Production Lines**: Developed a Python + Qt/C++ system to detect missing components in real time for a manufacturing customer.
- **Distributed Android Virtual Devices (Bosch Sub-company)**: Researched scalable deployment of Android applications in a cloud-based virtual environment.
- **Baseband Bus Software (Nokia)**: Maintained and incrementally improved an existing baseband bus software solution, ensuring reliability and long-term support.