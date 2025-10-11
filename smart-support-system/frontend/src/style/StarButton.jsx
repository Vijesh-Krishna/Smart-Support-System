// src/style/StarButton.jsx
import React from "react";
import { twMerge } from "tailwind-merge";

// ✅ Add glow animations globally once
const injectStarKeyframes = () => {
  if (document.getElementById("star-border-keyframes")) return;

  const style = document.createElement("style");
  style.id = "star-border-keyframes";
  style.innerHTML = `
    @keyframes star-movement-bottom {
      0% { transform: translate(0%, 0%); opacity: 1; }
      100% { transform: translate(-100%, 0%); opacity: 0; }
    }
    @keyframes star-movement-top {
      0% { transform: translate(0%, 0%); opacity: 1; }
      100% { transform: translate(100%, 0%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
};

const StarButton = ({
  as: Component = "button",
  className = "",
  color = "cyan",
  speed = "4s",
  thickness = 2,
  children,
  ...rest
}) => {
  React.useEffect(() => {
    injectStarKeyframes();
  }, []);

  return (
    <Component
      className={twMerge(
        "relative inline-block overflow-hidden rounded-[20px] transition-transform duration-300 hover:scale-[1.05] focus:outline-none",
        className
      )}
      style={{
        padding: `${thickness}px 0`,
        ...rest.style,
      }}
      {...rest}
    >
      {/* Glow bottom */}
      <div
        className="absolute w-[300%] h-[50%] opacity-80 bottom-[-12px] right-[-250%] rounded-full z-0 blur-xl"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 20%)`,
          animation: `star-movement-bottom ${speed} linear infinite alternate`,
        }}
      ></div>

      {/* Glow top */}
      <div
        className="absolute w-[300%] h-[50%] opacity-80 top-[-12px] left-[-250%] rounded-full z-0 blur-xl"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 20%)`,
          animation: `star-movement-top ${speed} linear infinite alternate`,
        }}
      ></div>

      {/* Actual button content */}
      <div className="relative z-10 backdrop-blur-md bg-black/30 border border-white/20 text-white text-center text-[16px] py-[14px] px-[24px] rounded-[20px] hover:bg-black/50">
        {children}
      </div>
    </Component>
  );
};

export default StarButton;
