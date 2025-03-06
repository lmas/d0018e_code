# D0018E, Databasteknik, V25

Creating a basic E-commerce site with a relational database.

|  Sprint ID |  Description                             |  Priority  |  Effort  |      Status     |
|  --------- |  -----------                             |  --------  |  ------  |      ------     |
| 1          | Minimal functional front- and backend    | High       | High     | Done            |
| 2          | Minimal functional e-commerce site       | Medium     | High     | Done            |
| 3          | Shopping basket                          | Low        | Medium   | In progress     |
| 3          | Grading and comment                      | Low        | Low      | In progress     |
| 4          | Fixups and complements                   | Low        | Low      | Project backlog |

Tech. stack:

- Database: MySQL
- Backend: Python Flask
- Frontend: HTML/CSS via Flask templates
- Web server: Nginx
- Host: Docker on an AWS EC2 instance

## Running

- Install `docker` and `docker-compose` (see OS specific guides of your own choice)
- Clone the repo: `git clone https://github.com/lmas/d0018e_code ./src`
- Create a local copy of the compose file: `cp ./src/docker-compose.yml .`
- Edit `docker-compose.yml` and add your own settings for database, ports, etc.
- Run all containers: `docker-compose up`
