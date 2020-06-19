import db from '@/models/index';
import getUserModel from '@/models/user';

const User = getUserModel(db.sequelize, db.Sequelize.DataTypes);

export default User;
