import { createContext, useState } from "react";
import React from "react";

export const SelectedPDFContext = createContext();

export function SelectedPDFProvider({ children }) {
    const [selectedPDFUrl, setSelectedPDFUrl] = useState(null);
    const [selectedPDFName, setSelectedPDFName] = useState(null);

    return (
        <SelectedPDFContext.Provider value={{
            selectedPDFUrl,
            setSelectedPDFUrl,
            selectedPDFName,
            setSelectedPDFName
        }}>
            {children}
        </SelectedPDFContext.Provider>
    );
}
