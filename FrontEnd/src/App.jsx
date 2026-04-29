import { useState } from "react";

export default function SafeContent() {
  const [disability, setDisability] = useState("ptsd");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState({ title: "", sections: [] });
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setResult({ title: "", sections: [] });
    setError(null);
    setStatus("מתחיל ניתוח...");

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), disability }),
      });

      if (!response.ok) throw new Error("הקשר עם השרת נכשל");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const chunk = JSON.parse(line);

            if (chunk.type === "status") {
              setStatus(chunk.message);
            }

            // (Streaming)
            // בתוך handleAnalyze -> while loop -> result update
            if (chunk.type === "data") {
              setResult((prev) => {
                const newSections = [...prev.sections];
                const incomingSections = chunk.chunk.sections || [];

                incomingSections.forEach((section, index) => {
                  if (newSections[index]) {
                    newSections[index] = {
                      ...newSections[index],
                      subtitle: section.subtitle || newSections[index].subtitle,
                      // שינוי כאן: דריסה במקום שרשור (+)
                      content: section.content || newSections[index].content,
                    };
                  } else {
                    newSections[index] = {
                      subtitle: section.subtitle || "",
                      content: section.content || "",
                    };
                  }
                });

                return {
                  title: chunk.chunk.title || prev.title,
                  sections: newSections,
                };
              });
            }

            // 🔹 סיום הסטרים
            if (chunk.type === "end") {
              setLoading(false);
              setStatus("הניתוח הושלם בהצלחה");
            }

            if (chunk.type === "error") {
              throw new Error(chunk.message);
            }
          } catch (e) {
            console.error("Parse error inside stream:", e);
          }
        }
      }
    } catch (err) {
      console.error("Request error:", err);
      setError(err.message);
      setLoading(false);
      setStatus("");
    }
  };

  const isPTSD = disability === "ptsd";

  return (
    <div
      dir="rtl"
      className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-200 text-right"
    >
      {/* NAVBAR */}
      <header className="fixed top-0 w-full backdrop-blur-xl bg-white/70 border-b border-slate-200 z-50 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <h1 className="text-xl font-extrabold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent tracking-tight">
            SafeContent
          </h1>

          <div className="flex gap-2 bg-white/60 p-1 rounded-full shadow-inner">
            {["ptsd", "anxiety"].map((m) => (
              <button
                key={m}
                onClick={() => setDisability(m)}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${
                  disability === m
                    ? m === "ptsd"
                      ? "bg-purple-500 text-white shadow-md"
                      : "bg-teal-500 text-white shadow-md"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {m === "ptsd" ? "פוסט טראומה" : "חרדה"}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="pt-28 pb-16 px-4 flex justify-center">
        <div className="w-full max-w-2xl">
          {/* HERO */}
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-slate-800 mb-3">
              ניתוח תוכן בטוח
            </h2>
            <p className="text-slate-500 text-base">
              {isPTSD
                ? "סינון תוכן רגיש והצגה עדינה ומבוקרת"
                : "הצגת תוכן בצורה רגועה וברורה"}
            </p>
          </div>

          {/* INPUT */}
          <div className="flex gap-3 mb-10">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && !loading && handleAnalyze()
              }
              placeholder="הכנס קישור לניתוח..."
              className="flex-1 px-5 py-4 rounded-2xl bg-white border border-slate-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-300 transition-all"
            />

            <button
              onClick={handleAnalyze}
              disabled={loading || !url.trim()}
              className={`px-6 py-4 rounded-2xl font-bold transition-all duration-300 ${
                loading || !url.trim()
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : isPTSD
                    ? "bg-purple-500 hover:bg-purple-600 text-white shadow-lg hover:scale-105"
                    : "bg-teal-500 hover:bg-teal-600 text-white shadow-lg hover:scale-105"
              }`}
            >
              {loading ? "טוען..." : "נתח"}
            </button>
          </div>

          {/* LOADING + STATUS */}
          {loading && (
            <div className="flex flex-col items-center gap-4 py-16 animate-fade-in">
              <div className="w-12 h-12 border-4 border-slate-200 border-t-purple-500 rounded-full animate-spin" />
              <p className="text-slate-600 text-sm animate-pulse">
                {status || "מנתח את הקישור..."}
              </p>
            </div>
          )}

          {/* ERROR */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-xl px-6 py-4 text-center text-sm mb-6">
              {error}
            </div>
          )}

          {/* RESULT */}
          {(result.title || result.sections.length > 0) && (
            <div className="space-y-6 animate-fade-in">
              {/* TITLE */}
              {result.title && (
                <div
                  className={`p-6 rounded-3xl border shadow-sm ${
                    isPTSD
                      ? "bg-purple-50 border-purple-200"
                      : "bg-teal-50 border-teal-200"
                  }`}
                >
                  <h3 className="text-2xl font-bold text-slate-800">
                    {result.title}
                  </h3>
                </div>
              )}

              {/* SECTIONS */}
              {result.sections.map((section, i) => (
                <div
                  key={i}
                  className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all"
                >
                  {section.subtitle && (
                    <h4 className="font-bold text-slate-700 mb-2">
                      {section.subtitle}
                    </h4>
                  )}
                  <p className="text-slate-600 leading-relaxed text-sm">
                    {section.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
