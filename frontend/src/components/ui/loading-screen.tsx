
import { motion } from "framer-motion";

export const LoadingScreen = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="fixed inset-0 z-50 flex items-center justify-center bg-background/90 backdrop-blur-lg"
  >
    <div className="relative">
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ 
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="h-24 w-24 rounded-full bg-gradient-to-tr from-primary to-secondary"
        />
      </div>
      
      <motion.div
        animate={{ 
          scale: [1, 0.9, 1],
          rotate: [0, -180, -360]
        }}
        transition={{ 
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="relative z-10 h-24 w-24 rounded-full bg-background"
      />
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ 
          opacity: [0, 1, 0],
          y: [0, -10, 0]
        }}
        transition={{ 
          duration: 1.5,
          repeat: Infinity,
          repeatDelay: 0.5
        }}
        className="absolute bottom-0 left-1/2 w-full -translate-x-1/2 translate-y-8 text-center"
      >
       
      </motion.div>
    </div>
  </motion.div>
);

export const LoadingSpinner = ({ size = "md" }: { size?: "sm" | "md" | "lg" }) => {
  const sizes = {
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-10 w-10",
  };
  
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
      className={`relative ${sizes[size]}`}
    >
      <div className="absolute inset-0 rounded-full border-4 border-t-transparent border-primary" />
      <div className="absolute inset-0 rounded-full border-4 border-b-transparent border-secondary opacity-30" />
    </motion.div>
  );
};