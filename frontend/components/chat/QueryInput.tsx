"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, AlertCircle } from "lucide-react";
import { containsPII } from "@/lib/pii";

const schema = z.object({
  query: z
    .string()
    .min(3, "Query must be at least 3 characters")
    .max(500, "Query must be under 500 characters")
    .refine((v) => !containsPII(v), {
      message: "Please do not include personal information (email, phone, PAN, Aadhaar).",
    }),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  defaultValue?: string;
}

export function QueryInput({ onSubmit, isLoading, placeholder, defaultValue }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { query: defaultValue ?? "" },
  });

  function submit(data: FormValues) {
    onSubmit(data.query);
    reset();
  }

  return (
    <form onSubmit={handleSubmit(submit)} className="flex flex-col gap-1">
      <div className="flex items-end gap-2">
        <textarea
          {...register("query")}
          disabled={isLoading}
          placeholder={
            placeholder ??
            "Ask about expense ratio, AUM, benchmark, holdings, risk rating, issuer…"
          }
          rows={1}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(submit)();
            }
          }}
          onInput={(e) => {
            const el = e.currentTarget;
            el.style.height = "auto";
            el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
          }}
          className="flex-1 rounded-button border border-border bg-surface px-4 py-3 text-[14px] placeholder:text-missing-gray focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 transition-shadow resize-none overflow-y-auto"
          style={{ minHeight: "44px", maxHeight: "120px" }}
          autoComplete="off"
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading}
          className="flex items-center justify-center w-11 h-11 rounded-button bg-primary-accent text-white hover:bg-primary-accent/90 disabled:opacity-50 transition-colors shrink-0"
          aria-label="Submit query"
        >
          <ArrowRight size={18} />
        </button>
      </div>
      {errors.query && (
        <div className="flex items-center gap-1.5 text-[12px] text-error-red">
          <AlertCircle size={12} />
          {errors.query.message}
        </div>
      )}
    </form>
  );
}
