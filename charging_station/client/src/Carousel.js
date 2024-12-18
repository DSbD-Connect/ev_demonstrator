import React, { useState, useEffect } from 'react';
import './Carousel.css'; // Make sure to create a CSS file for styles

const images = [
  'https://images.pexels.com/photos/191238/pexels-photo-191238.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
  'https://images.pexels.com/photos/1834403/pexels-photo-1834403.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
];

const Carousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 3000); // Change image every 3 seconds

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="carousel">
        <div className='carousel-ad-text'>Ad</div>
      <img src={images[currentIndex]} alt={`Slide ${currentIndex + 1}`} className="carousel-image" />
    </div>
  );
};

export default Carousel;