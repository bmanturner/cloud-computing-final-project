import User from '@/src';

export default async (req, res) => {
  const {
    method,
    body: {
      username = '',
      email = '',
      password = '',
    },
  } = req;

  if (method !== 'POST') {
    res.setHeader('Allow', ['POST'])
    return res.status(405).end(`method ${method} Not Allowed`)
  }

  try {
    const user = await User.create({ username, email, password });
    return res.json(user);
  } catch (e) {
    return res.json(e);
  }
}
