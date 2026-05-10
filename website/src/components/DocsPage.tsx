import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const modules = import.meta.glob("../docs/*.md", { query: "?raw", import: "default", eager: true }) as Record<string, string>;

const DOCS = Object.entries(modules).map(([path, content]) => {
  const slug = path.replace("../docs/", "").replace(".md", "");
  const title = slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return { slug, title, content };
});

export function DocsPage() {
  const [selected, setSelected] = useState(DOCS[0]?.slug ?? "");
  const doc = DOCS.find((d) => d.slug === selected);

  return (
    <div className="flex gap-8 max-w-5xl mx-auto px-6 py-10 w-full">
      <nav className="hidden sm:flex flex-col gap-1 w-44 shrink-0 pt-1">
        {DOCS.map((d) => (
          <button
            key={d.slug}
            onClick={() => setSelected(d.slug)}
            className={`text-left text-sm px-3 py-1.5 rounded transition-colors ${
              d.slug === selected
                ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium"
                : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
            }`}
          >
            {d.title}
          </button>
        ))}
      </nav>

      {/* mobile selector */}
      <div className="sm:hidden w-full mb-4">
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="w-full text-sm border border-gray-200 dark:border-gray-700 rounded px-3 py-1.5 bg-white dark:bg-gray-900"
        >
          {DOCS.map((d) => (
            <option key={d.slug} value={d.slug}>{d.title}</option>
          ))}
        </select>
      </div>

      <article className="flex-1 min-w-0 text-sm leading-relaxed text-gray-800 dark:text-gray-200">
        {doc ? (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold mt-8 mb-3 text-gray-900 dark:text-gray-100 first:mt-0">{children}</h1>,
              h2: ({ children }) => <h2 className="text-lg font-semibold mt-8 mb-2 text-gray-900 dark:text-gray-100">{children}</h2>,
              h3: ({ children }) => <h3 className="text-base font-semibold mt-6 mb-1 text-gray-900 dark:text-gray-100">{children}</h3>,
              p:  ({ children }) => <p className="mb-3">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-outside ml-5 mb-3 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-outside ml-5 mb-3 space-y-1">{children}</ol>,
              li: ({ children }) => <li>{children}</li>,
              blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-500 dark:text-gray-400 my-4">{children}</blockquote>,
              code: ({ children }) => <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
              pre:  ({ children }) => <pre className="bg-gray-100 dark:bg-gray-800 rounded p-4 overflow-x-auto mb-4 text-xs font-mono">{children}</pre>,
              a:    ({ href, children }) => <a href={href} className="underline text-blue-600 dark:text-blue-400 hover:opacity-80" target="_blank" rel="noopener noreferrer">{children}</a>,
              hr:   () => <hr className="border-gray-200 dark:border-gray-700 my-6" />,
              strong: ({ children }) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
            }}
          >
            {doc.content}
          </ReactMarkdown>
        ) : (
          <p className="text-gray-400">No document selected.</p>
        )}
      </article>
    </div>
  );
}
