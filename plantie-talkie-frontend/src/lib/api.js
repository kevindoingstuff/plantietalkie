import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const sendMessage = async (message) => {
  const response = await axios.post(`${API_URL}/plantie_talkie`, { user_input: message });
  return response.data;
};

export const waterPlant = async (plantId, moistureLevel = 50) => {
  const response = await axios.post(`${API_URL}/water_plant`, {
    plant_id: plantId,
    moisture_level: moistureLevel,
  });
  return response.data;
};

export const adjustLight = async (intensity) => {
  const response = await axios.post(`${API_URL}/adjust_light`, { intensity });
  return response.data;
};

export const getLogs = async () => {
  const response = await axios.get(`${API_URL}/logs`);
  return response.data;
};