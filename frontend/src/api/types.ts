// Mirrors backend/app/schemas/api.py
export type Role = 'student' | 'mentor';

export interface FieldInfo { key: string; label: string }

export interface Config {
  ai_mode: 'openrouter' | 'demo';
  ai_available: boolean;
  demo_login: boolean;
  supabase_url: string;
  supabase_publishable_key: string;
  mentor_fields: FieldInfo[];
  community_fields: FieldInfo[];
}

export interface User { id: string; name: string; role: Role }

export interface Me {
  status: 'active' | 'onboarding_required';
  user: User | null;
  suggested_name: string;
}

export interface Onboarding {
  role: Role;
  name: string;
  field?: string;
  bio?: string;
  hourly_rate_rupees?: number;
}

export type DemoAccount = 'student' | 'student_almost' | 'student_done' | 'mentor';

export interface Mentor {
  id: string;
  name: string;
  field: string;
  field_label: string;
  bio: string;
  hourly_rate_paise: number;
}

export interface OwnMentor extends Mentor { is_listed: boolean }

export interface Person { id: string; name: string }

export interface MentorshipRequest {
  id: string;
  status: 'pending' | 'accepted';
  student: Person;
  mentor: Person;
  created_at: string;
}

export interface Message {
  id: number;
  sender_name: string;
  mine: boolean;
  body: string;
  created_at: string;
}

export interface Conversation { request: MentorshipRequest; messages: Message[] }

export interface StudentBrief {
  name: string;
  field_label: string | null;
  summary: string;
  goals: string;
  guidance_needed: string;
  interests: string[];
  strengths: string[];
  mentor_focus: string;
  needs_human_followup: boolean;
}

export interface Post {
  id: number;
  author_name: string;
  author_role: Role;
  body: string;
  created_at: string;
}

export interface NewBooking {
  idempotency_key: string;
  mentor_id: string;
  minutes: number;
  topic: string;
  expected_rate_paise: number;
}

export interface Booking {
  id: string;
  student: Person;
  mentor: Person;
  request_id: string | null;
  hourly_rate_paise: number;
  minutes: number;
  total_paise: number;
  topic: string;
  status: 'pending' | 'confirmed';
  created_at: string;
}

export interface ChatMessage { role: 'user' | 'assistant'; content: string }

export interface CareerPath {
  id: string;
  title: string;
  category: string;
  streams: string[];
  route: string;
  overview: string;
}

export interface CareerExplorerInput {
  career_id: string;
  history: ChatMessage[];
  text: string;
}

export interface CareerExplorerReply { reply: string }

export interface Intake {
  status: 'not_started' | 'in_progress' | 'confirming' | 'ready_to_route' | 'completed';
  busy: boolean;
  can_retry: boolean;
  messages: ChatMessage[];
}

export interface Turn { reply: string; done: boolean; error: boolean; redirect_url: string | null }

export interface RoadmapStep { title: string; text: string }

export interface Dashboard {
  role: Role;
  field: string | null;
  field_label: string | null;
  roadmap: RoadmapStep[];
  intake_status: Intake['status'] | null;
  secondary_labels: string[];
  field_has_mentors: boolean;
  suggested_mentors: Mentor[];
  mentor: OwnMentor | null;
  requests: MentorshipRequest[];
  bookings: Booking[];
}
