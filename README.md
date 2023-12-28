MyDrive - A file sharing web app developed using Django
The file-sharing web application project aims to create a platform that allows users to securely upload, organize, and share files with others.
The scope encompasses user authentication, efficient file management including folder organization, collaboration features, and a secure trash system for deleted files.
The application's design prioritizes an intuitive user interface to enhance user experience, ensuring accessibility and ease of use.
The project has several key objectives. Firstly, it aims to implement core functionality for file upload, download, and basic management.
User collaboration features, such as secure file sharing, commenting, and version control, are crucial objectives.
The project also focuses on robust security measures, including data encryption and secure coding practices.
User management functionalities, like registration, login, and profile management, are integrated for a complete user experience.
Usability and user experience are emphasized through an intuitive interface.
Rigorous testing, comprehensive documentation, and scalability planning are additional objectives to ensure a high-quality, adaptable, and user-friendly file-sharing web application

To test it download the zip file or clone the repo on your local machine.

To install the frameworks, libraries and modules that you need run the command in your terminal.
-> pip install -r requirements.txt

In the root directory where 'manage.py' file is present run the command
-> python manage.py runserver

With this the web app should start at http://127.0.0.1:8000/.
You can now register and use it on your pc.

In case it does not work, run the commands
-> python manage.py makemigrations
-> python manage.py migrate
-> python manage.py runserver
