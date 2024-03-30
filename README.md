# web-app-contacts

## Python Anywhere deploy steps
1. create app on eu.pythonanywhere.com (Flask, default settings)
2. create ssh key
    - ssh-keygen -t ed25519 -C "your_email@example.com"
    - cat id_xxx.pub
    - copy, add to Github account
3. clone app repo in the home folder, near my_site
4. update 