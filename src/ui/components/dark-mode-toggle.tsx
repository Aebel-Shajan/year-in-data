// Example hook to toggle dark mode
import { useState, useEffect } from "react";
import { Switch } from "./ui/switch";

export default function DarkModeToggle() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <div className="flex items-center space-x-2 w-full justify-between">
      <label htmlFor="airplane-mode">Dark mode</label>
      <Switch id="airplane-mode" checked={dark} onCheckedChange={(checked: boolean) => setDark(checked)} />
    </div>
  )
}
