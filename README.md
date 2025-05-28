<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">DIGITAL-WALLET</h1></p>
<p align="center">
	<em>Digital-Wallet: Secure Your Transactions, Simplify Your Life!</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/yusuf-74/digital-wallet?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/yusuf-74/digital-wallet?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/yusuf-74/digital-wallet?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/yusuf-74/digital-wallet?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

## 🔗 Table of Contents

- [🔗 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#️-prerequisites)
  - [⚙️ Installation](#️-installation)
  - [🤖 Usage](#-usage)
  - [🧪 Testing](#-testing)
  - [📚 API Documentation](#-api-documentation)
  - [🧪 Testing](#-testing-1)
  - [📬 Postman Collection](#-postman-collection)

---

## 📍 Overview

The "Purpl Digital Wallet" project offers a secure and versatile solution for managing digital currencies and transactions. It features robust user authentication, multi-currency support, and tiered account functionalities, tailored for individuals and businesses seeking efficient financial management. This open-source platform is designed to streamline currency handling and enhance user transaction experiences.

---

## 👾 Features

|      |      Feature      | Summary                                                                                                                                                                                                                                                                                                                   |
| :--- | :---------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ⚙️    | **Architecture**  | <ul><li>Utilizes Docker for containerization, ensuring consistent environments across development, staging, and production.</li><li>Employs Nginx as a reverse proxy and load balancer to improve performance and reliability.</li></ul>                                                                                  |
| 🔩    | **Code Quality**  | <ul><li>Adopts Pythonic standards and best practices, facilitated by tools like flake8 and black for code formatting and linting.</li><li>Uses pytest for comprehensive testing, ensuring robustness.</li><li>Integrates pre-commit hooks to maintain code quality checks before commits are made.</li></ul>              |
| 📄    | **Documentation** | <ul><li>Documentation includes setup and usage instructions, leveraging markdown files for clarity and ease of use.</li><li>API documentation is managed with drf-spectacular, providing a clear schema for developers.</li></ul>                                                                                         |
| 🔌    | **Integrations**  | <ul><li>Integrates with various external services and APIs, including payment gateways and authentication services.</li><li>Uses Celery with Redis for task queue management, enabling asynchronous task processing.</li><li>Supports Docker for easy deployment and scalability across different environments.</li></ul> |
| 🧩    |  **Modularity**   | <ul><li>Highly modular design using Django apps for different features of the wallet.</li><li>Decouples business logic from the API layer, which enhances maintainability and scalability.</li><li>Utilizes Django REST framework to create clean, RESTful APIs for modular access to system features.</li></ul>          |
| 🧪    |    **Testing**    | <ul><li>Extensive use of pytest and pytest-django for backend testing, covering unit and integration tests.</li><li>Includes continuous integration setup to run tests automatically on various branches.</li><li>Uses pytest-cov to ensure adequate test coverage across modules.</li></ul>                              |
| ⚡️    |  **Performance**  | <ul><li>Utilizes database optimizations such as connection pooling via psycopg-pool.</li><li>Asynchronous task processing with Celery to improve overall efficiency of operations.</li></ul>                                                                                                                              |
| 🛡️    |   **Security**    | <ul><li>Implements security best practices including the use of Django’s built-in security features.</li><li>Uses JWT for secure authentication and authorization processes.</li></ul>                                                                                                                                    |

---

## 📁 Project Structure

```sh
└── digital-wallet/
    ├── Dockerfile
    ├── README.md
    ├── authentication
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   ├── 0001_initial.py
    │   │   ├── 0002_initial.py
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── signals.py
    │   ├── tasks.py
    │   ├── tests
    │   │   ├── __init__.py
    │   │   └── test_actions.py
    │   ├── urls.py
    │   └── views.py
    ├── conftest.py
    ├── core
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── auth
    │   │   ├── __init__.py
    │   │   ├── authentication.py
    │   │   └── permissions.py
    │   ├── base
    │   │   ├── serializers.py
    │   │   └── views.py
    │   ├── celery.py
    │   ├── config
    │   │   ├── __init__.py
    │   │   └── configuration_manager.py
    │   ├── middlewares
    │   │   ├── TimezoneMiddleware.py
    │   │   ├── __init__.py
    │   │   └── authenticated_swagger.py
    │   ├── routers.py
    │   ├── settings.py
    │   ├── test_settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── deploy.sh
    ├── deployments
    │   ├── docker-compose.local.yml
    │   ├── docker-compose.production.yml
    │   ├── docker-compose.staging.yml
    │   └── nginx
    │       ├── nginx.local.conf
    │       ├── nginx.production.conf
    │       └── nginx.staging.conf
    ├── manage.py
    ├── pyproject.toml
    ├── pytest.ini
    ├── requirements.txt
    ├── utilities
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── filters.py
    │   ├── migrations
    │   │   ├── 0001_initial.py
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── urls.py
    │   └── views.py
    ├── utils
    │   ├── __init__.py
    │   ├── cloud.py
    │   ├── common_tasks.py
    │   ├── custom_paginator.py
    │   ├── data_generators.py
    │   ├── orm_utils.py
    │   ├── pathes_generator.py
    │   └── validators.py
    └── wallets
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── events.py
        ├── filters.py
        ├── migrations
        │   ├── 0001_initial.py
        │   ├── 0002_tier_number_of_wallets.py
        │   ├── 0003_alter_tier_number_of_wallets.py
        │   └── __init__.py
        ├── models.py
        ├── serializers.py
        ├── tasks.py
        ├── tests
        │   └── test_actions.py
        ├── urls.py
        ├── utils.py
        └── views.py
```


### 📂 Project Index
<details open>
	<summary><b><code>DIGITAL-WALLET/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/conftest.py'>conftest.py</a></b></td>
				<td>- Conftest.py establishes a suite of fixtures for testing the application's API, focusing on user authentication, currency management, and wallet functionalities<br>- It configures various user scenarios and currency settings, enabling comprehensive testing of transaction limits and user interactions within different account tiers and currencies.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/pytest.ini'>pytest.ini</a></b></td>
				<td>- Configures pytest for the project by setting Django's test settings module and specifying file naming patterns for test discovery<br>- It also suppresses certain warnings during test runs, ensuring a cleaner output<br>- This configuration is essential for maintaining the efficiency and clarity of the testing process within the project's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/manage.py'>manage.py</a></b></td>
				<td>- Manage.py serves as the command-line interface for Django's administrative tasks, enabling environment setup and execution of various commands crucial for application management<br>- It ensures the Django framework is correctly imported and configured with the necessary settings before facilitating tasks such as database migrations, server start-up, and application testing.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td>- Manages and specifies the versions of all necessary libraries and dependencies required for the project's operation<br>- It ensures compatibility and stability across the development, testing, and production environments by locking down the versions of each package used in the Django-based web application framework.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/pyproject.toml'>pyproject.toml</a></b></td>
				<td>- Defines configuration settings for the "purpl-digital-wallet" project, specifying package metadata and code formatting rules<br>- It sets up Poetry for dependency management, Black and isort for code styling, and excludes certain files from formatting processes<br>- This configuration ensures consistent style and version management across the development team.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deploy.sh'>deploy.sh</a></b></td>
				<td>- Deploy.sh serves as a script for managing the deployment of Docker Compose stacks across different environments: production, staging, and local<br>- It automates the process of pulling the latest code, building, shutting down, and launching the appropriate Docker configurations based on the specified environment, ensuring streamlined and consistent deployment workflows.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/Dockerfile'>Dockerfile</a></b></td>
				<td>- Establishes the foundational environment for the application by using a Python base image and setting up a dedicated working directory<br>- It ensures all Python dependencies listed in `requirements.txt` are installed efficiently without storing extra cache, optimizing the build process for subsequent application development and deployment tasks within the project.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- core Submodule -->
		<summary><b>core</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/celery.py'>celery.py</a></b></td>
				<td>- Integrates Celery with Django for asynchronous task management within the core application<br>- It configures Celery to use Django settings, enabling task discovery across all Django apps<br>- A debug task is also defined to assist in monitoring Celery requests, enhancing the application's ability to handle background processes efficiently.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/routers.py'>routers.py</a></b></td>
				<td>- DBRouter in core/routers.py manages database interactions within the application, directing read operations to a replica database and write operations to the default database<br>- It ensures that relationships and migrations across different databases are permissible, enhancing the system's scalability and robustness by efficiently distributing database tasks.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/settings.py'>settings.py</a></b></td>
				<td>- Configures foundational settings for a Django-based application, managing environment variables, database connections, middleware, and installed apps<br>- It integrates security, performance, and development tools, setting up authentication, static and media management, and task scheduling to support a robust, scalable backend architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/test_settings.py'>test_settings.py</a></b></td>
				<td>- Configures essential settings for a Django-based application, managing environment-specific variables, database connections, middleware, and installed apps<br>- It integrates third-party tools for enhanced functionality and security, and sets up authentication, static files handling, and API settings to streamline development and deployment processes across different environments.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/urls.py'>urls.py</a></b></td>
				<td>- Core/urls.py serves as the central routing mechanism for the project, directing incoming URL requests to appropriate views and services<br>- It integrates administrative interfaces, API documentation, and user, wallet, and utility services, ensuring secure and structured access to the application's functionalities<br>- Additionally, it configures static file serving and optional debugging tools in development mode.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/asgi.py'>asgi.py</a></b></td>
				<td>- Configures and exposes the ASGI application for the core project, enabling asynchronous server gateway interface capabilities<br>- It sets up the necessary environment for Django's ASGI application to function, aligning with deployment best practices as outlined in Django's documentation<br>- This setup is crucial for handling asynchronous web requests within the project's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/wsgi.py'>wsgi.py</a></b></td>
				<td>- Configures the WSGI (Web Server Gateway Interface) for the core project, enabling the application to serve as a bridge between the web server and the Django application<br>- It sets up the necessary environment and declares the WSGI application callable, ensuring the project adheres to deployment best practices as outlined in Django documentation.</td>
			</tr>
			</table>
			<details>
				<summary><b>middlewares</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/middlewares/authenticated_swagger.py'>authenticated_swagger.py</a></b></td>
						<td>- AuthenticatedSwaggerView and AuthenticatedSchemaView in core/middlewares/authenticated_swagger.py ensure that only authenticated users can access the Swagger UI and API schema documentation<br>- These classes redirect unauthenticated users to the login page, enhancing the security of the API documentation within the Django-based application architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/middlewares/TimezoneMiddleware.py'>TimezoneMiddleware.py</a></b></td>
						<td>- TimezoneMiddleware dynamically adjusts the timezone for each request based on the 'X-Timezone' header<br>- It checks if the provided timezone is valid and sets it for the duration of the request, reverting to the default setting if not specified or invalid<br>- This ensures that all date and time data are correctly localized across the application.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>config</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/config/configuration_manager.py'>configuration_manager.py</a></b></td>
						<td>- ConfigurationManager serves as a centralized module for managing application settings, extracting environment-specific variables for API keys and database configurations<br>- It ensures seamless access to critical parameters like database credentials and API keys, facilitating secure and efficient connections across the application's components.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>base</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/base/views.py'>views.py</a></b></td>
						<td>- Centralizes response formatting across various API views within the codebase, ensuring a consistent structure with fields for success, message, data, and errors<br>- It enhances API responses for CRUD operations by integrating success and error messaging, thereby improving the clarity and reliability of client-server communication.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/base/serializers.py'>serializers.py</a></b></td>
						<td>- Core/base/serializers.py defines serializers that enhance data validation and handling in the application by automatically appending user-related metadata to model instances during creation and update processes<br>- It also customizes error responses to improve clarity and consistency in validation failure scenarios across the application's REST framework.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>auth</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/auth/authentication.py'>authentication.py</a></b></td>
						<td>- Implements custom API key authentication for securing API endpoints, ensuring that only requests with a valid API key gain access<br>- It integrates with Swagger for API documentation, defining security schemes and requirements for OpenAPI specifications, thereby enhancing API discoverability and security compliance within the project's architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/core/auth/permissions.py'>permissions.py</a></b></td>
						<td>- Manages access control in a RESTful API by defining permissions that restrict endpoint access based on API keys and user roles<br>- It ensures that only authenticated users or those with specific roles can perform actions like viewing, adding, changing, or deleting resources, enhancing security and compliance within the application architecture.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- utilities Submodule -->
		<summary><b>utilities</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/views.py'>views.py</a></b></td>
				<td>- Manages system messages and currency data through API views, ensuring appropriate access and updates<br>- It includes a health check endpoint to monitor system status<br>- The views handle authentication, optimize queries, and filter data based on user roles and permissions, enhancing both security and performance.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/apps.py'>apps.py</a></b></td>
				<td>- Defines the configuration for the 'utilities' module within the Django project, setting up essential parameters such as the default field type for database models<br>- It ensures that the utilities module is recognized and correctly integrated into the overall application, facilitating its management and scalability within the project's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/urls.py'>urls.py</a></b></td>
				<td>- Defines URL routing for key application functionalities within the utilities module, including system messages display, health status checks, and currency management<br>- It maps specific endpoints to views that handle the creation, retrieval, updating, and deletion of currency data, as well as system health and message retrieval operations.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/serializers.py'>serializers.py</a></b></td>
				<td>- Utilities/serializers.py defines serializers for the Currency and SystemMessage models, extending functionality from a base serializer<br>- It ensures these models are correctly transformed to and from data formats suitable for API responses, supporting comprehensive data handling across the system<br>- This setup is crucial for maintaining data integrity and facilitating smooth data operations within the application.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/filters.py'>filters.py</a></b></td>
				<td>- Defines and configures a filter set for the Currency model within a Django application, enabling refined searches based on currency name, currency code, and activity status<br>- It utilizes Django's filtering capabilities to enhance API query functionality, allowing users to perform precise and case-insensitive searches on currency attributes.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/admin.py'>admin.py</a></b></td>
				<td>- Registers key models, specifically Currency and SystemMessage, with Django's administration interface, enabling their management through the admin panel<br>- This setup facilitates easy oversight and manipulation of these models, crucial for maintaining system-wide messages and currency data within the application's administrative framework.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/models.py'>models.py</a></b></td>
				<td>- Defines data models for managing system messages and currencies within the application<br>- SystemMessage model handles notifications to user groups with attributes for timing and type, while Currency model tracks different currencies, ensuring unique identification and active status management<br>- Both models include fields for creation and last update tracking.</td>
			</tr>
			</table>
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utilities/migrations/0001_initial.py'>0001_initial.py</a></b></td>
						<td>- Establishes the foundational database schema for the project by creating two primary models: Currency and System Message<br>- Each model is equipped with fields tailored to store specific attributes and relationships, including references to user models for tracking updates, ensuring robust data management and integrity within the system.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- authentication Submodule -->
		<summary><b>authentication</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/views.py'>views.py</a></b></td>
				<td>- Manages user authentication and account operations within a Django-based application, including user registration, login, password reset, and phone number verification<br>- It utilizes Django REST framework views and serializers to handle requests and responses, ensuring users can securely manage their accounts.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/apps.py'>apps.py</a></b></td>
				<td>- Defines the configuration for the authentication module within a Django project, setting up essential parameters such as the database field type for automatically generated fields<br>- It also initializes signal handling specific to authentication processes, ensuring that custom signal listeners are active once the application is ready, thereby integrating seamlessly with the project's overall architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/signals.py'>signals.py</a></b></td>
				<td>- Handles the automatic creation of a default user profile upon new user registration within the system<br>- Specifically, it assigns a 'basic' tier to newly created users by leveraging Django's signal framework to trigger post-save actions on the User model, ensuring every new user has an initial tier set.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/tasks.py'>tasks.py</a></b></td>
				<td>- Manages the cleanup of outdated one-time password (OTP) codes within the authentication system by periodically deleting expired entries<br>- The task enhances security and optimizes database usage by ensuring only valid OTPs are stored, contributing to the overall efficiency and integrity of the authentication module.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/urls.py'>urls.py</a></b></td>
				<td>- Defines URL routing for user authentication and management within a Django application, linking endpoint paths to specific views handling user signup, login, phone verification, password operations, token refresh, and user details retrieval<br>- It facilitates both general user interactions and administrative access to user information.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/serializers.py'>serializers.py</a></b></td>
				<td>- Handles user-related data serialization and processing within the authentication system, including user creation, updates, and validation<br>- It supports operations like signing up, logging in, password management, and integrates user wallet and tier information, ensuring secure and efficient user data handling across the platform.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/admin.py'>admin.py</a></b></td>
				<td>- CustomUserAdmin in the authentication/admin.py enhances Django's admin interface by registering a customized User model and OTP model<br>- It modifies the admin panel to manage user attributes such as phone number, authentication status, and permissions more effectively, facilitating easier administration of user accounts and their verification statuses.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/models.py'>models.py</a></b></td>
				<td>- Defines user management and authentication models within a Django framework, including custom user creation and superuser setup with phone number identification and numeric password validation<br>- It also manages one-time passwords (OTPs) for user verification, ensuring uniqueness and time-limited validity to enhance security.</td>
			</tr>
			</table>
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/migrations/0001_initial.py'>0001_initial.py</a></b></td>
						<td>- Establishes the foundational database schema for user authentication within the system by creating models for 'OTP' and 'User'<br>- The 'OTP' model manages one-time passwords, including their validity and usage status, while the 'User' model handles user details, authentication credentials, and permissions, ensuring robust user management and security mechanisms.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/authentication/migrations/0002_initial.py'>0002_initial.py</a></b></td>
						<td>- Establishes foundational database schema modifications for the authentication system within the larger application architecture<br>- It integrates user tier levels linked to transaction limits and specific user permissions, enhancing user profile customization and security<br>- Additionally, it sets up a relationship for one-time password (OTP) management tied to user accounts, crucial for authentication processes.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- deployments Submodule -->
		<summary><b>deployments</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/docker-compose.staging.yml'>docker-compose.staging.yml</a></b></td>
				<td>- Orchestrates a staging environment for a Django-based application using Docker Compose, integrating services like Django, Celery, Redis, Nginx, and Certbot<br>- It manages application deployment tasks such as static file collection, database migrations, and server start-up, while ensuring services are interconnected and environment configurations are applied.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/docker-compose.production.yml'>docker-compose.production.yml</a></b></td>
				<td>- Orchestrates the deployment of a Django application in a production environment using Docker containers<br>- It configures services for the Django app, Celery workers and beat, Redis, Nginx, and Certbot, managing tasks from static file handling and database migrations to HTTPS certificate renewal, ensuring all components are interconnected and environment variables are correctly applied.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/docker-compose.local.yml'>docker-compose.local.yml</a></b></td>
				<td>- Establishes a local development environment using Docker, orchestrating multiple services including a Django application, PostgreSQL database, Redis, Celery workers, and Nginx<br>- It configures interdependencies among services, automates database migrations, and sets up a web server, ensuring a cohesive workflow for development and testing.</td>
			</tr>
			</table>
			<details>
				<summary><b>nginx</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/nginx/nginx.staging.conf'>nginx.staging.conf</a></b></td>
						<td>- Configures an Nginx server for the staging environment, setting up proxy rules to direct traffic to a Django application<br>- It adjusts connection limits and timeouts, and manages client body size restrictions to optimize performance and resource management under development conditions.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/nginx/nginx.local.conf'>nginx.local.conf</a></b></td>
						<td>- Configures an NGINX server to act as a reverse proxy, directing traffic to a Django application running locally<br>- It sets limits on worker connections and client body size, and customizes timeouts and headers to enhance the handling of forwarded requests, ensuring efficient communication between the client and the Django backend.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/deployments/nginx/nginx.production.conf'>nginx.production.conf</a></b></td>
						<td>- Configures the NGINX server for production environments, setting up proxy rules to direct traffic to a Django application<br>- It adjusts connection limits, timeouts, and body size restrictions to optimize performance and reliability, ensuring efficient handling of client requests and server responses within the broader system architecture.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- utils Submodule -->
		<summary><b>utils</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/validators.py'>validators.py</a></b></td>
				<td>- Validates URLs and domains within the application to ensure they conform to standard formats<br>- The module uses regular expressions to verify the structure of URLs and domains, raising exceptions for invalid entries<br>- This functionality supports the application's need for secure and correctly formatted web addresses, enhancing overall data integrity and security.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/custom_paginator.py'>custom_paginator.py</a></b></td>
				<td>- CustomPaginator, located in utils/custom_paginator.py, enhances pagination capabilities within the application by allowing dynamic page size adjustments based on user requests<br>- It supports returning entire querysets when specified, ensuring flexibility in data retrieval and display, which is crucial for handling varying client-side data consumption needs in the broader codebase architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/data_generators.py'>data_generators.py</a></b></td>
				<td>- Generates essential user-related data for various functionalities within the application<br>- It includes functions to create unique usernames by combining personal names with random numbers, secure passwords using a mix of characters, one-time passwords (OTPs), reference identifiers with timestamps and UUIDs, and unique wallet names based on currency type and existing names.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/pathes_generator.py'>pathes_generator.py</a></b></td>
				<td>- Generates unique file paths for user images within a Django-based application, utilizing a combination of the user's name and a random alphanumeric string to ensure uniqueness<br>- The function constructs a secure and SEO-friendly URL, storing the image in a designated public media directory, thus enhancing file management and retrieval efficiency across the system.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/common_tasks.py'>common_tasks.py</a></b></td>
				<td>- `utils/common_tasks.py` serves as a utility module within the broader codebase, enabling asynchronous communication functionalities<br>- It provides mechanisms to send emails and SMS messages, enhancing user interaction without blocking main application processes<br>- These tasks are essential for notifying users effectively, leveraging background processing to maintain application performance.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/cloud.py'>cloud.py</a></b></td>
				<td>- Manages secure access to AWS Secrets Manager, facilitating the retrieval of sensitive configurations based on deployment environments<br>- It supports both development and production settings, dynamically adjusting authentication methods<br>- The module also incorporates robust logging to track operations and handle potential errors efficiently.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/utils/orm_utils.py'>orm_utils.py</a></b></td>
				<td>- Optimizes database queries within a Django-based application by dynamically adjusting querysets based on request parameters<br>- It enhances performance by determining when to use `select_related` and `prefetch_related` methods for efficient data retrieval, and validates field requests to ensure only relevant data is fetched, reducing overhead and improving response times.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- wallets Submodule -->
		<summary><b>wallets</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/views.py'>views.py</a></b></td>
				<td>- Manages wallet and transaction functionalities within a Django-based application, enabling operations such as wallet creation, update, deactivation, and transaction handling including transfers and ATM code generation<br>- It ensures authenticated user access and optimizes database queries for efficiency.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/apps.py'>apps.py</a></b></td>
				<td>- Defines the configuration for the 'wallets' module within the Django project, setting up essential parameters such as the default field type for database entries<br>- It ensures the module is correctly recognized and integrated within the overall application, facilitating features related to financial transactions or wallet management in the system's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/utils.py'>utils.py</a></b></td>
				<td>- Manages financial transactions between wallets, including wallet-to-wallet transfers, ATM deposits and withdrawals, and bank transfers<br>- It ensures transaction integrity with atomic operations and enforces daily limits<br>- Additionally, it handles notifications for various transaction statuses, enhancing user communication through automated SMS alerts.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/tasks.py'>tasks.py</a></b></td>
				<td>- Resets daily spending limits for all user wallets by updating the transferred and withdrawn amounts to zero<br>- Scheduled as a daily task, it ensures accurate tracking of daily transactions by refreshing the spend counters<br>- The function concludes by reporting the total number of wallets updated, enhancing transparency and operational tracking within the system.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/urls.py'>urls.py</a></b></td>
				<td>- Defines URL routing for wallet-related functionalities within the Django application, linking endpoints to specific views handling operations like wallet creation, transaction listing, money transfers, and bank integrations<br>- It facilitates user interactions with the wallet system, enabling actions such as transferring funds, cancelling transactions, and retrieving ATM codes.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/serializers.py'>serializers.py</a></b></td>
				<td>- Wallets/serializers.py defines data serialization for wallet-related operations within a Django-based financial application<br>- It handles the conversion of wallet, transaction, and tier data to and from Python data types, supports dynamic data expansion based on query parameters, and enforces business logic through custom validation for transactions and wallet operations.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/events.py'>events.py</a></b></td>
				<td>- Handles ATM-related events within a banking application, managing deposit, withdrawal, and login operations through specific event handlers<br>- Each handler validates data, processes transactions, and sends notifications accordingly, ensuring transaction integrity and user feedback on operation success or failure.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/filters.py'>filters.py</a></b></td>
				<td>- Defines filtering capabilities for Wallet and Transaction models within a Django-based application, enabling refined searches based on user phone numbers, wallet attributes, and transaction specifics such as type, status, and source<br>- These filters facilitate user-friendly querying and management of financial records in the system.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/admin.py'>admin.py</a></b></td>
				<td>- Registers key models related to financial transactions and wallet management with the Django admin interface, enabling administrative oversight<br>- Models such as Wallet, Transaction, ATMCode, Tier, and TierCurrencyLimit are made accessible for admin tasks, facilitating the management of user accounts, transaction logs, access codes, account tiers, and currency limits within the system.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/models.py'>models.py</a></b></td>
				<td>- Defines and manages financial transactions and wallet functionalities within a Django-based application, including wallet creation, transaction processing, and ATM code generation<br>- It ensures data integrity through constraints and automates unique identifier generation for transactions and ATM codes, enhancing user financial interactions and security.</td>
			</tr>
			</table>
			<details>
				<summary><b>migrations</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/migrations/0001_initial.py'>0001_initial.py</a></b></td>
						<td>- Establishes the foundational database schema for the wallet management system, including models for user tiers, ATM codes, currency limits, wallets, and transactions<br>- It sets up relationships, constraints, and indices to ensure data integrity and optimize query performance within the financial platform.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/migrations/0003_alter_tier_number_of_wallets.py'>0003_alter_tier_number_of_wallets.py</a></b></td>
						<td>- Modifies the database schema within the 'wallets' module by updating the 'tier' model, specifically altering the 'number_of_wallets' field to have a new default value and associated help text<br>- This migration ensures the database accurately reflects the updated business rules regarding wallet allocations per tier.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/yusuf-74/digital-wallet/blob/master/wallets/migrations/0002_tier_number_of_wallets.py'>0002_tier_number_of_wallets.py</a></b></td>
						<td>- Introduces an additional integer field named 'number_of_wallets' to the 'tier' model within the wallets application, setting a default value and providing explanatory help text<br>- This migration, building on the initial database setup, specifies the maximum number of wallets permissible per tier, enhancing the application's capability to manage user access based on tier levels.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with digital-wallet, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip
- **Container Runtime:** Docker


### ⚙️ Installation

Install digital-wallet using one of the following methods:

**Build from source:**

1. Clone the digital-wallet repository:
```sh
❯ git clone https://github.com/yusuf-74/digital-wallet
```

2. Navigate to the project directory:
```sh
❯ cd digital-wallet
```

3. Install the project dependencies for local run:


**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r requirements.txt
```
<br />

OR

<br />

**Using `docker-compose`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker-compose -f deployments/docker-compose.local.yaml build
```




### 🤖 Usage
Run digital-wallet using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ python manage.py runserver
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker-compose -f deployments/docker-compose.local.yaml up --build
```


### 🧪 Testing
Run the test suite using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pytest
```

### 📚 API Documentation

Once the project is running, you can access the interactive API documentation at:

* **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/docs/)

> *Make sure `drf-yasg` or `drf-spectacular` is installed and configured to serve the docs at these endpoints.*

---

### 🧪 Testing

Run the test suite using the following command:

```sh
❯ pytest
```

---

### 📬 Postman Collection

A Postman collection is available to quickly test the available API endpoints.

* **Download:** [digital-wallet.postman\_collection.json](./Purplme-task.postman_collection.json)

> *Import this collection into Postman to try out the API endpoints easily.*