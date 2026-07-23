import React, { useState } from 'react';
import { waterPlant } from '../lib/api';

export default function WaterControl() {
  const [waterLevel, setWaterLevel] = useState(75);

  const handleWaterChange = (e) => {
    setWaterLevel(e.target.value);
  };

  const handleWaterPlant = async () => {
    try {
      const result = await waterPlant(1, Number(waterLevel));
      alert(result.message);
    } catch (error) {
      console.error('Error watering plant:', error);
      alert('Could not water the plant — is the backend running?');
    }
  };

  return (
    <div className="control-item">
      <h3 className="control-item__title">Water Control</h3>
      <div className="control-item__content">
        <input
          type="range"
          min="0"
          max="100"
          value={waterLevel}
          onChange={handleWaterChange}
          className="control-slider"
        />
        <div className="control-value">
          <span>{waterLevel}%</span>
        </div>
      </div>
      <div className="control-item__controls">
        <button
          onClick={handleWaterPlant}
          className="control-button"
        >
          Water Plant
        </button>
      </div>
    </div>
  );
}