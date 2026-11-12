
import React from "react";

interface CardLoaderProps {
  cards?: number;
  elementsPerCard?: number;
  className?: string;
  hasImage?: boolean;
  hasAction?: boolean;
}

export const CardLoader: React.FC<CardLoaderProps> = ({
  cards = 1,
  elementsPerCard = 3,
  className = "",
  hasImage = true,
  hasAction = true
}) => {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
      {Array.from({ length: cards }).map((_, cardIndex) => (
        <div 
          key={cardIndex}
          className="border border-border rounded-xl overflow-hidden shadow-sm animate-pulse"
          aria-label="Loading card"
        >
          {/* Image placeholder */}
          {hasImage && (
            <div className="bg-muted h-48 w-full" />
          )}
          
          <div className="p-5">
            {/* Titre */}
            <div className="h-6 bg-muted rounded w-3/4 mb-4" />
            
            {/* Éléments de contenu */}
            <div className="space-y-3">
              {Array.from({ length: elementsPerCard }).map((_, elementIndex) => (
                <div 
                  key={elementIndex}
                  className="h-4 bg-muted rounded"
                  style={{
                    width: `${80 - (elementIndex * 10)}%`,
                    opacity: 1 - (elementIndex * 0.15)
                  }}
                />
              ))}
            </div>
            
            {/* Boutons/Action */}
            {hasAction && (
              <div className="flex justify-between mt-6">
                <div className="h-10 bg-muted rounded-md w-24" />
                <div className="h-10 bg-muted rounded-md w-16" />
              </div>
            )}
          </div>
          
          {/* Pied de carte */}
          <div className="border-t border-border p-4 bg-muted/50">
            <div className="h-4 bg-muted rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
};