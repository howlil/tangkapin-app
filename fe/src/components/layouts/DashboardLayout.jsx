// src/components/DashboardLayout.js
import NavbarIndex from "./NavbarIndex";
import NavSideMobile from "./NavSideMobile";
import SidebarIndex from "./SidebarIndex";
import useMediaQuery from "../../hooks/useMediaQuery"

export default function DashboardLayout({ children }) {
  const isIpad = useMediaQuery("(min-width: 768px)");

  return (
    <>
      <aside className="md:block fixed hidden w-56 top-0 z-30 left-0 shadow-lg h-screen bg-white shadow-neutral-200">
        <SidebarIndex />
      </aside>
      <div>
        <nav
          className={` 
            ${isIpad ? "justify-end" : ""}
              shadow-sm fixed top-0 w-full p-4   md:pr-8  flex  z-20   right-0`}
        >
          {isIpad ? <NavbarIndex /> : <NavSideMobile />}
        </nav>
        <main className="h-full my-32 mx-4 md:ml-64 md:mr-8">
          {children}
        </main>
      </div>
    </>
  );
}
