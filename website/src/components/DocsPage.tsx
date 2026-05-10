import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { NotebookViewer, type NotebookData } from "./NotebookViewer";

const docModules = import.meta.glob("../docs/*.md", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const notebookModules = import.meta.glob("../../../notebooks/*.ipynb", { query: "?raw", import: "default", eager: true }) as Record<string, string>;

const DOCS = Object.entries(docModules).map(([path, content]) => {
  const slug = path.replace("../docs/", "").replace(".md", "");
  const title = slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return { slug, title, content };
});

const NOTEBOOKS = Object.entries(notebookModules).map(([path, raw]) => {
  const notebook = JSON.parse(raw) as NotebookData;
  const slug = path.split("/").pop()!.replace(".ipynb", "");
  const title = slug.replace(/^explore_/, "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return { slug, title, notebook };
});

type Selection = { kind: "doc"; slug: string } | { kind: "notebook"; slug: string };

const MD_COMPONENTS = {
  h1: ({ children }: React.PropsWithChildren) => <h1 className="text-2xl font-bold mt-8 mb-3 text-gray-900 dark:text-gray-100 first:mt-0">{children}</h1>,
  h2: ({ children }: React.PropsWithChildren) => <h2 className="text-lg font-semibold mt-8 mb-2 text-gray-900 dark:text-gray-100">{children}</h2>,
  h3: ({ children }: React.PropsWithChildren) => <h3 className="text-base font-semibold mt-6 mb-1 text-gray-900 dark:text-gray-100">{children}</h3>,
  p:  ({ children }: React.PropsWithChildren) => <p className="mb-3">{children}</p>,
  ul: ({ children }: React.PropsWithChildren) => <ul className="list-disc list-outside ml-5 mb-3 space-y-1">{children}</ul>,
  ol: ({ children }: React.PropsWithChildren) => <ol className="list-decimal list-outside ml-5 mb-3 space-y-1">{children}</ol>,
  li: ({ children }: React.PropsWithChildren) => <li>{children}</li>,
  blockquote: ({ children }: React.PropsWithChildren) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-500 dark:text-gray-400 my-4">{children}</blockquote>,
  code: ({ children }: React.PropsWithChildren) => <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
  pre:  ({ children }: React.PropsWithChildren) => <pre className="bg-gray-100 dark:bg-gray-800 rounded p-4 overflow-x-auto mb-4 text-xs font-mono">{children}</pre>,
  a:    ({ href, children }: React.PropsWithChildren<{ href?: string }>) => <a href={href} className="underline text-blue-600 dark:text-blue-400 hover:opacity-80" target="_blank" rel="noopener noreferrer">{children}</a>,
  hr:   () => <hr className="border-gray-200 dark:border-gray-700 my-6" />,
  strong: ({ children }: React.PropsWithChildren) => <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>,
};

function NavButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`text-left text-sm px-3 py-1.5 rounded transition-colors ${
        active
          ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-medium"
          : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
      }`}
    >
      {label}
    </button>
  );
}

export function DocsPage() {
  const [selection, setSelection] = useState<Selection>({ kind: "doc", slug: DOCS[0]?.slug ?? "" });

  const content = (() => {
    if (selection.kind === "doc") {
      const doc = DOCS.find((d) => d.slug === selection.slug);
      if (!doc) return null;
      return (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
          {doc.content}
        </ReactMarkdown>
      );
    }
    const nb = NOTEBOOKS.find((n) => n.slug === selection.slug);
    if (!nb) return null;
    return <NotebookViewer notebook={nb.notebook} />;
  })();

  const mobileValue = `${selection.kind}:${selection.slug}`;

  return (
    <div className="flex gap-8 max-w-5xl px-6 py-10 w-full">
      {/* desktop sidebar */}
      <nav className="hidden sm:flex flex-col gap-0.5 w-44 shrink-0 pt-1">
        {DOCS.length > 0 && (
          <>
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 px-3 mb-1">Docs</p>
            {DOCS.map((d) => (
              <NavButton
                key={d.slug}
                label={d.title}
                active={selection.kind === "doc" && selection.slug === d.slug}
                onClick={() => setSelection({ kind: "doc", slug: d.slug })}
              />
            ))}
          </>
        )}

        {NOTEBOOKS.length > 0 && (
          <>
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 px-3 mt-4 mb-1">Notebooks</p>
            {NOTEBOOKS.map((n) => (
              <NavButton
                key={n.slug}
                label={n.title}
                active={selection.kind === "notebook" && selection.slug === n.slug}
                onClick={() => setSelection({ kind: "notebook", slug: n.slug })}
              />
            ))}
          </>
        )}
      </nav>

      {/* mobile dropdown */}
      <div className="sm:hidden w-full mb-4">
        <select
          value={mobileValue}
          onChange={(e) => {
            const [kind, slug] = e.target.value.split(":") as ["doc" | "notebook", string];
            setSelection({ kind, slug });
          }}
          className="w-full text-sm border border-gray-200 dark:border-gray-700 rounded px-3 py-1.5 bg-white dark:bg-gray-900"
        >
          <optgroup label="Docs">
            {DOCS.map((d) => <option key={d.slug} value={`doc:${d.slug}`}>{d.title}</option>)}
          </optgroup>
          <optgroup label="Notebooks">
            {NOTEBOOKS.map((n) => <option key={n.slug} value={`notebook:${n.slug}`}>{n.title}</option>)}
          </optgroup>
        </select>
      </div>

      <article className="flex-1 min-w-0 text-sm leading-relaxed text-gray-800 dark:text-gray-200">
        {content ?? <p className="text-gray-400">Nothing selected.</p>}
      </article>
    </div>
  );
}
