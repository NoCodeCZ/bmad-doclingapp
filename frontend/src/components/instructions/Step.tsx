'use client';

import Image from 'next/image';
import { useState } from 'react';

interface StepProps {
  number: number;
  title: string;
  description: string;
  imagePath: string;
  imageAlt: string;
}

export function Step({ number, title, description, imagePath, imageAlt }: StepProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  return (
    <li className="relative">
      <div className="flex gap-4 md:gap-6">
        {/* Step Number */}
        <div className="flex-shrink-0">
          <div className="flex items-center justify-center w-10 h-10 md:w-12 md:h-12 bg-primary text-primary-foreground rounded-full font-bold text-lg md:text-xl">
            {number}
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 space-y-4">
          <div>
            <h3 className="text-xl md:text-2xl font-semibold mb-2">{title}</h3>
            <p className="text-muted-foreground leading-relaxed">{description}</p>
          </div>

          {/* Screenshot */}
          <div className="relative w-full max-w-2xl">
            {!imageError ? (
              <div className="relative bg-muted rounded-lg overflow-hidden border border-border">
                {!imageLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center bg-muted">
                    <div className="text-muted-foreground text-sm">Loading image...</div>
                  </div>
                )}
                <Image
                  src={imagePath}
                  alt={imageAlt}
                  width={800}
                  height={450}
                  className="w-full h-auto"
                  loading="lazy"
                  onLoad={() => setImageLoaded(true)}
                  onError={() => setImageError(true)}
                />
              </div>
            ) : (
              <div className="bg-muted border border-dashed border-border rounded-lg p-8 text-center">
                <div className="text-muted-foreground space-y-2">
                  <div className="text-4xl">📸</div>
                  <p className="text-sm">Screenshot placeholder</p>
                  <p className="text-xs">Image will be added: {imagePath}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Connector Line */}
      {number < 6 && (
        <div className="absolute left-5 md:left-6 top-12 md:top-14 w-0.5 h-full bg-border" />
      )}
    </li>
  );
}
