# Responsive Design Quick Reference

## Screen Size Overview

Mobile      Tablet         Desktop        Large Desktop
320px       768px          1024px         1280px+
├───────────┼──────────────┼──────────────┼──────────────►
   sm           md             lg             xl

## Common Responsive Patterns

### Sidebar Navigation

- **Mobile (< 768px)**: Hidden by default, opens as slide-in overlay
- **Desktop (≥ 768px)**: Always visible, sticky sidebar

### Typography

// Heading sizes
<h1 className="text-xl md:text-2xl lg:text-3xl">

// Body text
<p className="text-sm md:text-base">

// Small text
<span className="text-xs md:text-sm">

```



<div className="p-3 md:p-4 lg:p-6">

// Gap between elements
<div className="gap-3 md:gap-4 lg:gap-6">

// Vertical spacing
<div className="space-y-3 md:space-y-4">
```

### Grid Layouts

```tsx
// 2-column responsive
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">

// 3-column responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// 4-column responsive
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

// Or use utility classes
<div className="grid-responsive-3 gap-responsive">
```

### Forms

```tsx
// Form container
<form className="form-responsive">
  
  // Field group
  <div className="space-y-1.5 md:space-y-2">
    <Label>Field Name</Label>
    <Input />
    <p className="text-xs md:text-sm text-muted-foreground">Help text</p>
  </div>
  
</form>
```

### Buttons

```tsx
// Full width on mobile, auto on desktop
<Button className="w-full md:w-auto">

// Responsive size
<Button size="sm" className="text-xs md:text-sm">
```

### Tables

```tsx
// Auto horizontal scroll on mobile
<div className="overflow-x-auto">
  <Table>
    {/* Table content */}
  </Table>
</div>
```

### Cards

```tsx
// Card grid (1-4 columns based on screen)
<div className="card-grid">
  <Card>...</Card>
  <Card>...</Card>
  <Card>...</Card>
</div>
```

### Container

```tsx
// Responsive container with padding
<div className="container-responsive">
  {/* Content */}
</div>
```

## Hide/Show Elements

```tsx
// Hidden on mobile, visible on desktop
<div className="hidden md:block">

// Visible on mobile, hidden on desktop
<div className="block md:hidden">

// Inline flex responsive
<div className="hidden md:inline-flex">
```

## Responsive Images

```tsx
// Responsive image
<img 
  className="w-full h-auto max-w-sm md:max-w-md lg:max-w-lg"
  src="image.jpg"
  alt="Description"
/>
```

## Flexbox Responsive

```tsx
// Stack on mobile, row on desktop
<div className="flex flex-col md:flex-row gap-4">

// Reverse order on mobile
<div className="flex flex-col-reverse sm:flex-row">

// Center on mobile, space-between on desktop
<div className="flex flex-col items-center md:flex-row md:justify-between">
```

## Component-Specific Patterns

### Navigation Bar

```tsx
<header className="sticky top-0 z-10 border-b">
  <div className="flex items-center justify-between px-4 py-3">
    {/* Mobile menu button */}
    <Button className="md:hidden" onClick={toggleMenu}>
      <Menu />
    </Button>
    
    {/* Logo */}
    <h1 className="text-base md:text-lg">Logo</h1>
    
    {/* Desktop nav items */}
    <nav className="hidden md:flex gap-4">
      <a href="#">Link 1</a>
      <a href="#">Link 2</a>
    </nav>
  </div>
</header>
```

### Modal/Dialog

```tsx
<Dialog>
  <DialogContent className="max-w-[calc(100%-2rem)] sm:max-w-lg">
    <DialogHeader>
      <DialogTitle className="text-lg md:text-xl">Title</DialogTitle>
    </DialogHeader>
    
    <DialogFooter className="flex-col-reverse sm:flex-row">
      <Button variant="outline">Cancel</Button>
      <Button>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

## Testing Tips

1. **Chrome DevTools**: Toggle device toolbar (Cmd/Ctrl + Shift + M)
2. **Responsive Design Mode**: Test at 320px, 768px, 1024px, 1280px
3. **Touch Targets**: Ensure minimum 44x44px for interactive elements
4. **Text Readability**: Check font sizes are readable without zoom
5. **Horizontal Scroll**: Tables and wide content should scroll, not break layout

## Performance Considerations

- Use `hidden md:block` instead of conditional rendering when possible
- Minimize layout shifts between breakpoints
- Test on actual devices, not just emulators
- Optimize images for mobile (use responsive images or next/image)

## Accessibility

- Ensure keyboard navigation works at all breakpoints
- Touch targets are large enough (44x44px minimum)
- Text has sufficient contrast at all sizes
- Screen readers can access all content regardless of breakpoint
