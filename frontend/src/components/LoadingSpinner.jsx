import React, { useState } from 'react'
 
const LoadingSpinner = () => {
 
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-6">
      <div className="w-10 h-10 border-4 border-[#DDD0B3] border-t-[#2F4A3B] rounded-full animate-spin" />
      <p className="text-[#4A4436] font-medium tracking-wide">
        Processing Document.......
      </p>
    </div>
  )
}
 
export default LoadingSpinner
 