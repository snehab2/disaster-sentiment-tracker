import React from "react";

// import "./SearchResult.css";
export default function SearchResult( {result}) {
    return (
    <div 
        className = "search-result"
        onClick = {(e) => alert(`You clicked on ${result.name}`)} // Route this to the correct disaster
    >
        {result.name}
    </div>
    );
}