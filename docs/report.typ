
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2.5cm),
  numbering: "1",
)
#set text(
  font: "Linux Libertine",
  size: 11pt,
  lang: "en",
)
#set par(
  justify: true,
  leading: 0.65em,
)
#set heading(numbering: "1.1")

// Title Page
#align(center + horizon)[
  #text(size: 24pt, weight: "bold")[KDE Connect Web Client]\
  #v(1cm)
  #text(size: 18pt)[Semester Report]\
  #v(2cm)
  #text(size: 14pt)[Vaisakh KM]\
  #text(size: 12pt)[BITS Pilani]\
  #v(1cm)
  #text(size: 12pt)[#datetime.today().display()]
]

#pagebreak()

#outline(indent: auto)
#pagebreak()

= INTRODUCTION

KDE Connect has established itself as a cornerstone of the open-source ecosystem, providing a robust solution for bridging the gap between diverse operating systems and hardware platforms. Designed to enable a seamless multi-device experience, it allows smartphones, tablets, and desktop computers to communicate securely over a local network. At its core, the project facilitates a synchronized workflow where users can share clipboards, mirror notifications, control multimedia playback remotely, and transfer files effortlessly between devices. Currently, the ecosystem is predominantly supported by native applications developed for Qt-based desktops (spanning Linux, Windows, and macOS), as well as mobile applications for Android and iOS.

However, the reliance on native applications presents a barrier to entry in environments where software installation is restricted or impossible. The current project aims to evolve this ecosystem by developing a dedicated **KDE Connect Web Client**. This initiative is fundamentally driven by the need to extend these powerful integration features to "zero-install" environments. By creating a solution that runs a lightweight embedded server on a primary device and exposes a responsive web interface, the project allows any modern browser to act as a fully functional KDE Connect node. This effectively transforms any device with internet browsing capabilities—such as a Chromebook, a public library computer, or a guest workstation—into an integral part of the user's unified digital workflow.

The evolution of web technologies, particularly the capabilities of modern browsers to handle complex networking and state management, makes this the perfect time to explore such a solution. Unlike traditional web pages, modern web applications can maintain persistent connections, handle binary data for file transfers, and render complex user interfaces that rival native desktop applications. This project leverages these capabilities to replicate the native KDE Connect experience within the constraints of a browser sandbox.

Throughout this comprehensive report, we will explore the technical journey of building this web client. We will delve into the specific usability gaps that motivated the project, the architecture of the REST API designed to abstract the underlying protocol, and the implementation of core plugins like Ping, Battery Status, and Notification management. The project not only seeks to solve a technical limitation but also to significantly increase the adoption of KDE Connect in professional and public spheres by removing the friction of installation. This semester's work represents a significant step toward a truly platform-agnostic device integration framework.

= PROBLEM STATEMENT

The central challenge addressed by this project is the significant "usability gap" created by KDE Connect’s reliance on native application installations. Currently, the software operates on a strictly peer-to-peer basis where every participating node—whether a phone, tablet, or PC—must have the KDE Connect binary installed and running locally to communicate with other devices. While this architecture works exceptionally well for personal hardware where the user has full administrative control, it becomes a major roadblock in restricted digital environments.

Consider the following scenarios:
- **Corporate Environments:** Users frequently work on corporate laptops with locked-down administrative privileges. IT policies often strictly prohibit the installation of unauthorized software, effectively preventing the user from installing the KDE Connect desktop client.
- **Public Workstations:** In universities, libraries, or internet cafes, users rely on shared computers where they cannot install software. In these scenarios, the user is effectively cut off from their integrated workflow, unable to sync clipboards or receive critical phone notifications on their active screen.
- **Guest Devices:** When borrowing a colleague's laptop for a quick presentation or task, installing a full synchronization suite is impractical and intrusive.

Furthermore, the diversity of modern computing platforms includes "thin client" style devices and operating systems, such as ChromeOS or various lightweight web-based kiosks, where native support for Qt-based applications is either non-existent or requires complex, resource-intensive workarounds (like Linux containers). For a user who relies on KDE Connect for productivity, the inability to access these features on a secondary device without a lengthy setup process reduces the overall utility of the ecosystem. This requirement for installation on every single device decreases the convenience that KDE Connect promises, leading to lower adoption rates among users who move frequently between different hardware environments.

To resolve this, there is a clear need for a client that requires **zero installation** on the secondary device. The problem is not just about connectivity, but about **accessibility**. By failing to provide a web-based entry point, KDE Connect misses the opportunity to serve users in the most common "on-the-go" computing situations. The project seeks to solve this by shifting the architectural burden: instead of requiring a native client on both ends, we propose a system where one primary device hosts an embedded server, allowing any browser-capable device to bridge the gap and rejoin the user's unified digital workspace.

= OBJECTIVES OF THE PROJECT

The objectives of this project are multi-faceted, ranging from core functionality to ensuring a high-quality user experience.

== Primary Objective: The Web Client
The primary objective is to architect and implement a high-performance, responsive web client that serves as a universal gateway to the KDE Connect ecosystem. Unlike traditional clients that require local binary execution, this project aims to leverage a lightweight embedded server—running on a primary "host" device—to expose KDE Connect’s rich feature set via standard web protocols (HTTP/WebSocket). By doing so, the project seeks to eliminate the dependency on platform-specific installation for secondary devices, ensuring that any device equipped with a modern web browser can participate in the user's integrated environment without administrative overhead.

== Secondary Objective: Plugin Porting
A critical secondary objective involves the successful porting and exposure of core KDE Connect plugins into a web-compatible format. This includes the development of a robust REST API capable of handling complex interactions. Key plugins targeted for this implementation include:
- **Ping Plugin:** To verify connectivity and latency between devices.
- **Notification Plugin:** To support real-time notification mirroring from the host to the web client.
- **Share Plugin:** To enable file transfers, specifically receiving files from remote devices.
- **Battery Plugin:** To monitor the battery status of connected devices.
- **Run Command Plugin:** To execute predefined remote commands.

The goal is to ensure that the user experience through the browser is as seamless and responsive as the native application experience. This requires careful management of the backend server logic to handle multiple requests without compromising the performance of the host device.

== Tertiary Objective: Security and Scalability
Finally, the project is committed to establishing a secure and scalable foundation for future enhancements. This includes implementing a secure pairing mechanism that adheres to the established KDE Connect protocol (RSA key exchange) while adapting to the unique security constraints of a browser environment. The objective is not merely to create a "view-only" dashboard, but a functional interactive tool. By the end of this semester, the project intends to deliver a documented, stable, and user-friendly web interface that can be deployed across various restricted network environments to improve user productivity.

= BACKGROUND OF PREVIOUS WORK

The development of a web client for KDE Connect is built upon the robust foundation of the KDE Connect protocol, which has been an open-source standard for cross-device integration for over a decade.

== The KDE Connect Protocol
Traditionally, work in this area has focused on native applications built using the Qt framework for desktop environments like Linux, Windows, and macOS, alongside mobile applications for Android and iOS. These existing implementations rely on a peer-to-peer communication model where devices discover each other over a local network using UDP broadcast packets (typically on port 1716) and establish encrypted TCP connections (typically on port 1764) for data exchange. While highly effective, this traditional approach necessitates that every device in the network runs a full native stack of the KDE Connect software.

== Headless Implementations
In recent years, specialized community projects have attempted to decouple the KDE Connect logic from its heavy desktop dependencies to allow for "headless" operations. A notable example is the `kdeconnect-webapp` project, which was designed to allow non-interactive environments, such as servers or command-line-only systems, to interact with the KDE Connect ecosystem. This previous work introduced the concept of a lightweight daemon (`kdeconnect-webapp-d`) that could handle the protocol's identity announcements and pairing requests without needing a graphical user interface.

== Current Technological Context
Technically, previous iterations utilized Python-based virtual environments to manage dependencies and leveraged specific libraries like `requests` and `PIL` for client-side interactions and image processing. These projects highlighted the importance of port management. However, most of these previous efforts were focused on a CLI-first or server-to-device interaction model rather than a fully realized, browser-based graphical user interface for end-users.

This project takes those foundational concepts—the REST API and the headless daemon—and extends them into a responsive, user-facing web client. By utilizing modern frontend frameworks and responsive design principles, we aim to bridge the gap between the raw protocol and the end-user, creating a tool that is both powerful and accessible.

= POTENTIAL CHALLENGES & RISKS

One of the most significant technical challenges facing this project is maintaining compatibility with the evolving KDE Connect protocol.

== Protocol Versioning
Recent updates to the KDE Connect ecosystem, such as the transition to desktop version 25.03.80 and Android version 1.33.0, have introduced protocol changes that increase security but also break backward compatibility with older, "untrusted" devices. For instance, if a device was initially installed with an Android version older than 1.24.0, its device ID might be too short for the current protocol, necessitating a complete reset of app data to allow for successful re-pairing. Ensuring that the web client's embedded server can dynamically handle these protocol shifts—sending identity packets that match specific version requirements—is a critical risk factor for maintaining a stable connection.

== Network Infrastructure and Security
Network and security infrastructure poses another substantial risk to the project's deployment. KDE Connect relies heavily on specific network ports, such as:
- **Port 1716:** Used for UDP broadcast discovery and TCP signaling.
- **Port 1764:** Used for secure service communication and data transfer.

In the very environments where this web client is most needed—such as corporate offices or public institutions—firewalls and network isolation policies often block these ports by default. Furthermore, since the web client communicates over TCP/IP, any network jitter or aggressive "AP Isolation" settings on public Wi-Fi could prevent the browser from discovering the host device. This requires the development of robust error handling and perhaps manual IP entry fallbacks to ensure reliability.

== Resource Constraints
Finally, there is a risk regarding the resource consumption and security of the host device. Running a lightweight embedded server on a primary device (like a smartphone) to serve a web interface introduces additional CPU and battery overhead.
- **Performance:** If not optimized, the server could negatively impact the host's performance.
- **Security:** The "admin-port" (often defaulting to 8080) exposes the REST API. If not properly secured or bound to the correct interface, it could become a target for unauthorized access.
Balancing ease of access with strict security measures—such as ensuring that only paired and trusted devices can execute remote commands—is essential to prevent the web client from becoming a vulnerability in the user’s personal network.

= REQUIREMENTS & USE CASE MODELS

### 6.1 Functional Requirements

The functional requirements of the KDE Connect Web Client are centered on replicating the core interactive capabilities of the native application within a browser-based environment.

- **Device Discovery and Pairing:** The system must allow the web-based node to announce its identity and establish a secure, encrypted handshake with other devices on the network.
- **Notification Management:** The client must be able to receive mirrored notifications from a phone and send custom alerts from the web interface to other devices.
- **Remote Execution and Utilities:**
  - **"Run commands" plugin:** Triggers pre-defined scripts on a remote PC.
  - **"Host remote commands":** Allows other devices to trigger actions on the server hosting the web client.
  - **"Ping" and "Ring my phone":** Essential utility functions to help users locate their devices and verify network connectivity.
- **File Handling:** The system must include the ability to receive files sent from other devices and save them locally via the browser's download manager.

### 6.2 Non-Functional Requirements

Non-functional requirements focus on the performance, usability, and security of the application.

- **Portability and Accessibility:** The web client must be compatible with all modern, standards-compliant browsers (Chrome, Firefox, Safari, Edge) without requiring any plugins or extensions.
- **Responsiveness:** The user interface must adapt seamlessly to different screen sizes, from small smartphone displays to large desktop monitors.
- **Security and Low Latency:** All communication between the web browser and the host server should ideally be encrypted, and the administrative port must be protected.
- **Lightweight Footprint:** The backend server must utilize minimal system resources (CPU and RAM) to ensure it can run in the background without draining the battery.
- **Error Feedback:** The application should provide clear feedback if a device goes offline or if a firewall is blocking necessary ports.

### 6.3 Use Case Model

The Use Case Model for this project describes the interactions between the "Guest User" (the actor) and the "Web Client System."

- **Remote Device Interaction:** A user at a public terminal logs into the web client URL, selects their paired smartphone from a list, and clicks "Ring Device" to find it.
- **Cross-Platform Notification Mirroring:** The system automatically updates the web dashboard whenever the host device receives a message, allowing the user to stay informed without checking their physical phone.
- **Pairing Use Case:** This involves a multi-step verification process where the web client sends an identity packet, the host device displays a pairing request, and the user confirms the link on both ends.
- **File Reception Use Case:** The web client listens for incoming data streams and prompts the browser to download the file once the transfer is complete.

= RESOURCES NEEDED

#### 7.1 Hardware Resources
The implementation and deployment of the KDE Connect Web Client require a multi-tiered hardware setup to simulate real-world usage.
- **Host Device:** Typically a user's primary workstation or smartphone. This device must have sufficient processing power to run the background daemon and the web server simultaneously.
- **Secondary Devices:** Restricted environments such as a Chromebook, a tablet, or a secondary PC where native software installation is blocked.

#### 7.2 Software Resources
The software architecture is heavily reliant on the Python ecosystem and modern web technologies.
- **Backend:** Python 3, using libraries like `requests` and `PIL`, managed within a virtual environment (`venv`).
- **Frontend:** HTML5, CSS3, and JavaScript creating a responsive dashboard.
- **Tools:** `build` and `twine` for packaging.

#### 7.3 Networking Resources
Reliable network infrastructure is critical.
- **Ports:** 1716 (Discovery/UDP), 1764 (Service/TCP), 8080 (REST API).
- **Environment:** Local Area Network (LAN) or shared Wi-Fi connection allowing bidirectional communication.

#### 7.4 Human Resources
The project relies on a single-developer model supported by the broader open-source community.
- **Developer:** Vaisakh KM (Backend API, Frontend Design, Documentation).
- **Community:** KDE Community (Bug reports, Protocol documentation) and Academic Supervisors (Peer reviews).

= DETAILED PLAN OF WORK DONE

The execution of the KDE Connect Web Client project was divided into distinct phases.

== Phase 1: Research and Environment Setup
During the initial weeks, the focus was on establishing a stable Python-based development environment. This involved:
- Setting up virtual environments (`venv`) to isolate dependencies.
- Deep dive into the KDE Connect protocol specifications to understand identity packets and encryption key exchange.
- Troubleshooting discovery issues related to protocol version mismatches, ensuring the web server could mimic desktop version 25.03.80.

== Phase 2: Backend Development (Headless Daemon)
The second phase centered on the development of the "headless" daemon and the REST API.
- Implemented `kdeconnect-webapp-d` server.
- Handled network discovery on port 1716 and service communication on port 1764.
- Mapped API endpoints to core plugins: "Ping", "Ring My Phone", "Run Commands".
- Refined the Command-Line Interface (CLI) for manual testing.

== Phase 3: Frontend Development and Integration
The final phase involved the creation of the web-based user interface.
- Built a dynamic frontend interacting with the REST API.
- Implemented the "Receive" plugin for file transfers.
- Conducted extensive testing for "Host remote commands".
- Resulted in a functional prototype bridging native capabilities and browser accessibility.

= FUTURE WORK & EXTENSION OR SCOPE OF IMPROVEMENTS

While the current version is functional, there is significant room for expansion.

- **Bidirectional File Sharing:** Implementing file uploads from the browser to paired devices using multi-part form data.
- **Progressive Web App (PWA):** Enhancing the UI/UX to allow installation on mobile home screens with offline capabilities.
- **Advanced Plugins:** Implementing shared clipboard history, remote input control, and media player synchronization.
- **Automation:** Creating system service files (systemd/launchd) for automatic startup.
- **Enhanced Security:** Implementing OAuth2 or hardware-backed authentication for the administrative port to allow secure exposure over the internet.

= INFERENCES / SUMMARY

The development of the KDE Connect Web Client represents a critical pivot toward universal accessibility in device integration. The key inference is that the limitations of native software installation can be effectively bypassed by leveraging a headless backend paired with a RESTful web interface. By abstracting the complex peer-to-peer logic of the KDE Connect protocol into a manageable API, the project has demonstrated that even highly restricted environments can participate in a unified digital workflow.

The project also highlights the resilience of the KDE Connect protocol. Despite challenges with versioning, the ability to mimic modern identity packets ensures continued relevance. The semester’s work confirms that a lightweight Python-based server can provide a high-performance experience with minimal latency.

= CONCLUSIONS AND RECOMMENDATIONS

The completion of the KDE Connect Web Client project concludes that likely providing a browser-based interface is a highly viable and necessary solution for modern multi-device integration. The "barrier of installation" is one of the greatest obstacles to widespread adoption. By abstracting the protocol into a web dashboard, we have proved that users can maintain workflows in restricted environments without compromising security.

**Recommendations:**
- **Network Configuration:** Ensure firewall rules allow traffic on ports 1716 and 1764.
- **Device Compatibility:** Use Android 1.24.0+ for best ID compatibility.
- **Development:** Use Python virtual environments for dependency management.
- **Community:** Consider an official "Headless Mode" in the main KDE Connect branch.

= DIRECTIONS FOR FUTURE WORK

The successful deployment of the current prototype opens several avenues for expansion.

- **WebRTC/WebSocket Support:** For truly real-time, low-latency updates (remote mouse control, clipboard syncing).
- **Cloud Relay Discovery:** Developing a secure relay server to allow devices to find each other over the internet (requires TLS).
- **Multi-User Environments:** Implementing a multi-tenant architecture for educational institutions or small businesses.

= BIBLIOGRAPHY & REFERENCES

+ **KDE Connect Community.** (2024). *KDE Connect Protocol Specification and Wiki.* Available at: https://community.kde.org/KDEConnect
+ **Metallkopf.** (2024). *KDE Connect Webapp: Headless Server and REST API Implementation.* GitHub Repository.
+ **Python Software Foundation.** (2024). *Virtual Environments (venv) and Package Management.* Python 3.x Documentation.
+ **Google Developers.** (2024). *Responsive Web Design Fundamentals and PWA Best Practices.* Web.dev Documentation.
+ **KDE Project.** (2024). *Release Notes for Desktop Version 25.03.80 and Android Version 1.33.0.*

