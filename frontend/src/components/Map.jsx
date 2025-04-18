import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css"; // Import Leaflet CSS
import ToolTip from "./ToolTip";

export default function Map({location}) {

  const paragraph = "Generated by an AI model using related posts. Content may not always be accurate."
  const mapContainerRef = useRef(null); // Reference the div, not the map instance
  const mapInstanceRef = useRef(null); // Store the map instance separately

  useEffect(() => {
    if (!mapInstanceRef.current && mapContainerRef.current) {
      mapInstanceRef.current = L.map(mapContainerRef.current).setView([location.latitude, location.longitude], 10); // Corrected UTD location

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
      }).addTo(mapInstanceRef.current);

      L.circle([location.latitude, location.longitude], {
        color: 'red',
        fillColor: '#f03',
        fillOpacity: 0.5,
        radius: location.radius
      }).addTo(mapInstanceRef.current);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove(); // Cleanup
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (

    <div className="flex flex-col border border-[#D4D4D4] rounded-md mt-5 md:mt-15 text-left p-4 gap-y-2 h-[25rem] w-full">
        <div className="border-b-1 border-[#D4D4D4] pb-2">
          <div className="flex flex-row gap-x-2 items-center justify-between">
            <h3>Location of Disaster</h3>
            <ToolTip paragraph={paragraph}/>
          </div>
        </div>
      {location ? (
        <div ref={mapContainerRef} className="flex-1 w-full h-0"></div>
      ) : (
        <div className="flex flex-wrap justify-center items-center leading-80">No data</div>
      )}
      
    </div>
  );
}


// need to run: npm install leaflet react-leaflet