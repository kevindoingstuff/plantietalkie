import React, { useState } from 'react';
import { adjustLight } from '../lib/api';

export default function LightControl() {
  const [lightLevel, setLightLevel] = useState(50);

  const handleLightChange = (e) => {
    setLightLevel(e.target.value);
  };

  const handleAdjustLight = async () => {
    try {
      const result = await adjustLight(lightLevel);
      alert(result.message);
    } catch (error) {
      console.error('Error adjusting light:', error);
      alert('Could not adjust the light — is the backend running?');
    }
  };

  return (
    <div className="control-item">
      <h3 className="control-item__title">Light Control</h3>
      <div className="control-item__content">
        <input
          type="range"
          min="0"
          max="100"
          value={lightLevel}
          onChange={handleLightChange}
          className="control-slider"
        />
        <div className="control-value">
          <span>{lightLevel}%</span>
        </div>
      </div>
      <div className="control-item__controls">
        <button onClick={handleAdjustLight} className="control-button">
          Adjust Light
        </button>
      </div>
    </div>
  );
}