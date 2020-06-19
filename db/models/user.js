const { Sequelize } = require('sequelize');

'use strict';
module.exports = (sequelize, DataTypes) => {
  const User = sequelize.define('User', {
    username: {
      type: DataTypes.STRING,
      unique: true,
      allowNull: false,
      validate: {
        isAlphanumeric: true,
        len: [4, 32],
      }
    },
    email: {
      type: DataTypes.STRING,
      unique: true,
      allowNull: false,
      validate: {
        isEmail: true,
      }
    },
    password: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        len: [5, 32],
        notContains: ' ',
      },
    },
    apiKey: {
      type: DataTypes.UUID,
      allowNull: false,
      defaultValue: Sequelize.UUIDV4,
      validate: {
        isUUID: 4,
      },
    }
  }, {
    underscored: true,
    tableName: 'Users',
  });
  User.associate = function(models) {
    // associations can be defined here
  };
  return User;
};