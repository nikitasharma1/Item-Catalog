# Item Catelog

This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered have the ability to post, edit and delete their own items.

## Prerequisites

- Python version **version 2.7.12** or _later_.
- Flask **version 0.12.2** or _later_.

## Get Started

- Clone the repository on the local machine.

```
$ git clone https://github.com/nikitasharma1/Item-Catalog.git
```

- or_ download the _.zip_ file [here](https://github.com/nikitasharma1/Item-Catalog/archive/master.zip)

- Run script **database_setup.py**.

```
$ python database_setup.py
```

- Run script **dummy_data.py** to populate database with dummy data.

```
$ python dummy_data.py
```

- Connect to server at ```http://localhost:5000``` from browser.

## Status:

1. Currently, login/signup only by Google Plus is available.
2. Logged in users can create categories and items.
3. Logged in users can update and delete their own items.
4. Available API endpoints [here](https://github.com/nikitasharma1/Item-Catalog/blob/master/api_list.txt)

## Acknowledgments

- [Udacity](https://in.udacity.com/course/full-stack-web-developer-nanodegree--nd004/)

## License

This project is licensed under the [MIT](LICENSE.md)  License.
