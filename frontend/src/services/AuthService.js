import axios from 'axios';

const API_URL = 'http://localhost:5000/api/auth/';

class AuthService {
  login(user) {
    return axios
      .post(API_URL + 'login', {
        email: user.email,
        password: user.password
      })
      .then(response => {
        if (response.data.access_token) {
          localStorage.setItem('user', JSON.stringify(response.data));
        }
        return response.data;
      });
  }

  logout() {
    localStorage.removeItem('user');
  }

  register(user) {
    return axios.post(API_URL + 'register', {
      email: user.email,
      password: user.password,
      name: user.name,
      role: user.role,
      address: user.address,
      pin: user.pin,
      service_type: user.service_type,
      experience: user.experience
    });
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  }

  getToken() {
    const user = this.getCurrentUser();
    return user ? user.access_token : null;
  }
}

export default new AuthService(); 