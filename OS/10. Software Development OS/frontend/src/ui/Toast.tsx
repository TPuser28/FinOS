import * as React from "react"
import { cn } from "../lib/utils"
import { X } from "lucide-react"

interface ToastProps {
  message: string
  type?: "success" | "error" | "info"
  onClose: () => void
  className?: string
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ message, type = "info", onClose, className }, ref) => {
    const [isVisible, setIsVisible] = React.useState(true)

    React.useEffect(() => {
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(onClose, 300) // Wait for fade out animation
      }, 5000)

      return () => clearTimeout(timer)
    }, [onClose])

    const handleClose = () => {
      setIsVisible(false)
      setTimeout(onClose, 300)
    }

    const typeStyles = {
      success: "bg-green-500 text-white",
      error: "bg-red-500 text-white",
      info: "bg-blue-500 text-white"
    }

    return (
      <div
        ref={ref}
        className={cn(
          "fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg transition-all duration-300",
          typeStyles[type],
          isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2",
          className
        )}
      >
        <span className="text-sm font-medium">{message}</span>
        <button
          onClick={handleClose}
          className="ml-2 text-white/80 hover:text-white transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    )
  }
)
Toast.displayName = "Toast"

export { Toast }
