import React from 'react';
import WaterControl from './WaterControl';
import LightControl from './LightControl';

export default function PlantControl({ className }) {
  return (
    <div 
      className={`plant-control ${className || ''}`}
    >
      <h2 className="plant-control__title">Controller Module</h2>
      <div className="plant-control__content">
        <WaterControl />
        <LightControl />
      </div>
    </div>
  );
}