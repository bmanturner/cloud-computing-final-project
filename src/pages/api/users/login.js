import User from '@/src/user';

export default async (req, res) => {
  const {
    method,
    body: {
      username,
      password,
    },
  } = req;

  if (method !== 'POST') {
    res.setHeader('Allow', ['POST'])
    return res.status(405).end(`method ${method} Not Allowed`)
  }

  const user = await User.findOne({ where: { username, password } });

  return res.json(user);
};