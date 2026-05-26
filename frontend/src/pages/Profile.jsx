import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { DNASpinner } from "../components/DNASpinner";
import { GlowButton, Pill } from "../components/Interactive";
import { useProfileStore, useUIStore, useUserStore } from "../stores/useStores";
import { profileService } from "../services/profileService";

const allergyOptions = ["Nuts", "Gluten", "Dairy", "Soy", "Eggs", "Shellfish", "Peanuts", "Fish"];
const conditionOptions = ["Diabetes", "Hypertension", "Heart Disease", "Pregnant", "Kidney Disease", "Celiac Disease", "Lactose Intolerant", "None"];
const dietOptions = ["Vegan", "Vegetarian", "None"];

function Section({ icon, title, children }) {
  return (
    <motion.section initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mt-9">
      <h2 className="inline-flex items-center gap-3 font-orbitron text-lg font-bold text-mint">{icon} {title}</h2>
      <motion.div initial={{ width: 0 }} whileInView={{ width: "100%" }} viewport={{ once: true }} className="mt-2 h-px bg-gradient-to-r from-mint to-transparent" />
      <div className="mt-5 flex flex-wrap gap-3">{children}</div>
    </motion.section>
  );
}

export default function Profile() {
  const profile = useProfileStore();
  const toast = useUIStore((state) => state.toast);
  const accessToken = useUserStore((state) => state.accessToken);
  const navigate = useNavigate();
  const [customOpen, setCustomOpen] = useState(false);
  const [custom, setCustom] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const toggle = (key, value) => {
    const current = profile[key];
    profile.updateProfile({ [key]: current.includes(value) ? current.filter((item) => item !== value) : [...current, value] });
  };

  const save = async () => {
    setSaving(true);
    const next = { allergies: profile.allergies, health_conditions: profile.healthConditions, diet_type: profile.dietType };
    if (custom.trim()) next.allergies = [...new Set([...next.allergies, custom.trim()])];
    profile.updateProfile({ allergies: next.allergies, healthConditions: next.health_conditions, dietType: next.diet_type });
    if (accessToken) {
      try {
        await profileService.save(next);
      } catch {
        // Anonymous/local profile still works if backend is not running.
      }
    }
    setSaving(false);
    setSaved(true);
    toast({ type: "success", title: "Profile saved", message: "Your AI guardian is tuned." });
    window.setTimeout(() => navigate("/scanner"), 650);
  };

  return (
    <PageTransition>
      <div className="mx-auto max-w-[680px]">
        <div className="text-center">
          <h1 className="font-orbitron text-3xl font-black md:text-5xl">Personalize Your AI Guardian</h1>
          <p className="mt-4 text-slate">Tell us about your health so we can protect you specifically.</p>
        </div>
        <div className={`glass relative mt-10 overflow-hidden p-6 md:p-9 ${saved ? "ring-2 ring-mint" : ""}`}>
          <div className="absolute inset-x-0 top-0 h-[3px] bg-gradient-to-r from-mint to-violet" />
          <div className="mx-auto grid h-20 w-20 place-items-center rounded-3xl bg-mint/15 text-4xl text-mint animate-float">♙</div>
          <Section icon="!" title="Allergies">
            {allergyOptions.map((item) => <Pill key={item} selected={profile.allergies.includes(item)} onClick={() => toggle("allergies", item)}>{item}</Pill>)}
            <Pill selected={customOpen} onClick={() => setCustomOpen(!customOpen)}>+ Add Custom Allergy</Pill>
            <motion.div initial={false} animate={{ height: customOpen ? "auto" : 0, opacity: customOpen ? 1 : 0 }} className="basis-full overflow-hidden">
              <input value={custom} onChange={(e) => setCustom(e.target.value)} className="focus-glow mt-3 w-full rounded-2xl border border-mint/20 bg-ocean/80 px-4 py-4 text-ice placeholder:text-slate" placeholder="Enter custom allergy" />
            </motion.div>
          </Section>
          <Section icon="⌁" title="Health Conditions">
            {conditionOptions.map((item) => <Pill key={item} selected={profile.healthConditions.includes(item)} onClick={() => toggle("healthConditions", item)}>{item}</Pill>)}
          </Section>
          <Section icon="☘" title="Diet Type">
            {dietOptions.map((item) => <Pill key={item} single selected={profile.dietType === item} onClick={() => profile.updateProfile({ dietType: item })}>{item}</Pill>)}
          </Section>
          <GlowButton onClick={save} className={`mt-10 w-full rounded-2xl ${saved ? "bg-mint" : ""}`} disabled={saving}>
            {saving ? <span className="flex justify-center"><DNASpinner /></span> : saved ? "✓ Saved" : "Save Profile and Continue"}
          </GlowButton>
        </div>
      </div>
    </PageTransition>
  );
}
