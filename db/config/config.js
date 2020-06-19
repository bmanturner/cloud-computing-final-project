require('dotenv').config();

const {
  DB_HOST,
  DB_NAME,
  DB_USERNAME,
  DB_PASSWORD,
} = process.env;

module.exports = {
  development: {
    username: DB_USERNAME,
    password: DB_PASSWORD,
    database: DB_NAME,
    host: DB_HOST,
    dialect: 'mysql'
  },
};
